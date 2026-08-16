"""
Human AI Trainer Grade Review & Community Nickname Routes
"""

import os
import json
import time as _time
from datetime import datetime as _dt
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Form, Depends
from google.cloud import firestore
from schemas.grade_review_schemas import GradeReviewSubmission, NicknameSubmitRequest
from routes.deps import db, logger, get_current_user_email

router = APIRouter(prefix="/api", tags=["Human AI Trainer & Community Grade Reviews"])

# Shared constants
LOW_CONFIDENCE_THRESHOLD = 0.85

# In-memory stats cache for eventual consistency
GRADE_STATS_CACHE: Dict[str, Any] = {}
GRADE_WRITE_TIMESTAMPS: Dict[str, float] = {}

@router.get("/grade_review/queue")
def grade_review_queue(user_email: str, limit: int = 30):
    """
    Returns the user's own AI-graded coins that haven't been reviewed yet,
    sorted by confidence_score ascending (lowest = most urgently needs review).
    """
    coins_ref = db.collection('users').document(user_email).collection('coins')

    seen_ids: set = set()
    raw_docs: list = []
    
    try:
        q = coins_ref.where('grade_review_status', '==', 'pending').limit(200).stream()
        for doc in q:
            if doc.id not in seen_ids:
                seen_ids.add(doc.id)
                raw_docs.append(doc)
    except Exception as e:
        logger.exception("Grade review queue query failed")

    results = []
    for doc in raw_docs:
        d      = doc.to_dict()
        source = d.get('source', '')
        conf_val = d.get('confidence_score')
        conf   = float(conf_val) if conf_val is not None else 1.0

        reviews = d.get('grade_reviews', [])
        if any((isinstance(r, dict) and r.get('reviewer') == user_email) or (isinstance(r, str) and r == user_email) for r in reviews):
            continue

        results.append({
            'coin_id':             doc.id,
            'year':                d.get('Year', ''),
            'mint_mark':           d.get('Mint Mark', ''),
            'denomination':        d.get('Denomination', ''),
            'program_series':      d.get('Program/Series', ''),
            'theme_subject':       d.get('Theme/Subject', ''),
            'condition':           d.get('Condition', 'Ungraded'),
            'ai_assigned_condition': d.get('ai_assigned_condition',
                                          d.get('Condition', 'Ungraded')),
            'confidence_score':    round(conf, 2),
            'low_confidence':      conf < LOW_CONFIDENCE_THRESHOLD,
            'source':              source,
            'scan_source':         d.get('scan_source', source),
            'image_url_obverse':   d.get('image_url_obverse', ''),
            'image_url_reverse':   d.get('image_url_reverse', ''),
            'slot_bbox':           d.get('slot_bbox', {}),
            'grade_review_status': d.get('grade_review_status', 'pending'),
            'grade_review_count':  d.get('grade_review_count', 0),
        })

    results.sort(key=lambda x: x['confidence_score'])
    return {
        'status':  'ok',
        'results': results[:limit],
        'total':   len(results),
    }

@router.post("/grade_review/submit")
async def submit_grade_review(
    user_email:      str = Form(...),
    coin_id:         str = Form(...),
    action:          str = Form(...),
    suggested_grade: str = Form(''),
    rating:          int = Form(...),
    notes:           str = Form(''),
):
    """
    Record a grade review on one of the user's own coins.
    If 2/3+ of reviews disagree with the AI grade, flagged for admin review.
    """
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")
    if action not in ('confirmed', 'corrected'):
        raise HTTPException(status_code=400, detail="Action must be 'confirmed' or 'corrected'.")
    if action == 'corrected' and not suggested_grade.strip():
        raise HTTPException(status_code=400, detail="suggested_grade is required when action=corrected.")

    coins_ref = db.collection('users').document(user_email).collection('coins')
    coin_ref  = coins_ref.document(coin_id)
    coin_doc  = coin_ref.get()
    if not coin_doc.exists:
        raise HTTPException(status_code=404, detail="Coin not found.")

    d = coin_doc.to_dict()

    reviews = list(d.get('grade_reviews', []))
    if any((isinstance(r, dict) and r.get('reviewer') == user_email) or (isinstance(r, str) and r == user_email) for r in reviews):
        raise HTTPException(status_code=400, detail="You have already reviewed this coin.")

    ai_assigned = d.get('ai_assigned_condition') or d.get('Condition', 'Ungraded')

    reviews.append({
        'reviewer':        user_email,
        'action':          action,
        'suggested_grade': suggested_grade.strip() if action == 'corrected' else '',
        'rating':          rating,
        'notes':           notes.strip(),
        'reviewed_at':     _dt.utcnow().isoformat(),
    })

    if action == 'corrected':
        try:
            hitl_log_path = os.path.join(os.path.dirname(__file__), "..", 'data', 'hitl_training_corrections.json')
            log_entries = []
            if os.path.exists(hitl_log_path):
                with open(hitl_log_path, 'r', encoding='utf-8') as f:
                    log_entries = json.load(f)
            log_entries.append({
                'coin_id': coin_id,
                'user_email': user_email,
                'original_ai_grade': ai_assigned,
                'human_suggested_grade': suggested_grade.strip(),
                'notes': notes.strip(),
                'timestamp': _dt.utcnow().isoformat()
            })
            with open(hitl_log_path, 'w', encoding='utf-8') as f:
                json.dump(log_entries, f, indent=2)
        except Exception as log_err:
            logger.warning(f"HITL training log write error: {log_err}")

        try:
            corr_id = f"hitl_{int(_time.time())}_{coin_id[:8]}"
            corr_data = {
                "schema_version": "1.0",
                "correction_id": corr_id,
                "task_type": "visual_grade",
                "coin_id": coin_id,
                "user_email": user_email,
                "original_ai_output": {"grade": ai_assigned},
                "verified_output": {"grade": suggested_grade.strip(), "notes": notes.strip()},
                "consensus_status": "pending",
                "consensus_ratio": 1.0,
                "created_at": _dt.utcnow().isoformat()
            }
            if db:
                db.collection("hitl_training_corrections").document(corr_id).set(corr_data, merge=True)
        except Exception as dbe:
            logger.warning(f"Firestore HITL write error: {dbe}")

    review_count  = len(reviews)
    dict_reviews  = [r for r in reviews if isinstance(r, dict)]
    corrections   = [r for r in dict_reviews if r.get('action') == 'corrected']
    confirmations = [r for r in dict_reviews if r.get('action') == 'confirmed']

    new_status     = 'pending'
    grade_consensus = ''
    flagged        = False

    if review_count >= 3:
        correction_ratio = len(corrections) / review_count
        if correction_ratio >= 0.67:
            grade_counts: dict = {}
            for r in corrections:
                g = r.get('suggested_grade', '')
                if g:
                    grade_counts[g] = grade_counts.get(g, 0) + 1
            if grade_counts:
                grade_consensus = max(grade_counts, key=grade_counts.get)
            new_status = 'flagged_for_admin_review'
            flagged    = True
        elif len(confirmations) / review_count >= 0.75:
            new_status = 'confirmed'

    update_payload: dict = {
        'grade_reviews':         reviews,
        'grade_review_count':    review_count,
        'grade_review_status':   new_status,
        'ai_assigned_condition': ai_assigned,
    }
    if grade_consensus:
        update_payload['grade_consensus'] = grade_consensus

    if flagged:
        db.collection('admin_grade_flags').document(coin_id).set({
            'user_email':        user_email,
            'coin_id':           coin_id,
            'ai_assigned_grade': ai_assigned,
            'community_grade':   grade_consensus,
            'review_count':      review_count,
            'flagged_at':        firestore.SERVER_TIMESTAMP,
            'resolved':          False,
            'year':              d.get('Year', ''),
            'mint_mark':         d.get('Mint Mark', ''),
            'program_series':    d.get('Program/Series', ''),
        }, merge=True)

    coin_ref.set(update_payload, merge=True)

    msg = '✓ Grade confirmed! Thank you for helping improve Numista.AI.' if action == 'confirmed' else f'Correction submitted -- "{suggested_grade}" has been noted.'
    if flagged and action != 'confirmed':
        msg += ' 🚩 Community consensus differs from the AI grade -- this coin has been flagged for admin review.'

    GRADE_WRITE_TIMESTAMPS[user_email] = _time.time()
    cache_entry = GRADE_STATS_CACHE.get(user_email)
    if cache_entry:
        stats = cache_entry.get("stats", {})
        stats["reviewed_by_me"] = stats.get("reviewed_by_me", 0) + 1
        stats["pending_review"] = max(0, stats.get("pending_review", 0) - 1)
        stats["total_ai_graded"] = stats["pending_review"] + stats["reviewed_by_me"]
        if action == 'confirmed':
            stats["confirmed"] = stats.get("confirmed", 0) + 1
        elif flagged:
            stats["flagged"] = stats.get("flagged", 0) + 1
        GRADE_STATS_CACHE[user_email] = {
            "stats": stats,
            "timestamp": _time.time()
        }

    return {
        'status':       'ok',
        'message':      msg,
        'new_status':   new_status,
        'review_count': review_count,
        'flagged':      flagged,
    }

@router.get("/admin/grade_flags")
def admin_grade_flags(resolved: bool = False, limit: int = 100):
    """Returns all coins flagged for admin grade review."""
    try:
        q = (db.collection('admin_grade_flags')
               .where('resolved', '==', resolved)
               .order_by('flagged_at', direction=firestore.Query.DESCENDING)
               .limit(limit))
        docs = list(q.stream())
    except Exception:
        docs = list(
            db.collection('admin_grade_flags')
              .where('resolved', '==', resolved)
              .limit(limit)
              .stream()
        )

    flags = []
    for doc in docs:
        d = doc.to_dict()
        try:
            owner  = d.get('user_email', '')
            cid    = d.get('coin_id', doc.id)
            cdoc   = (db.collection('users').document(owner)
                        .collection('coins').document(cid).get())
            img    = cdoc.to_dict().get('image_url_obverse', '') if cdoc.exists else ''
            conf   = cdoc.to_dict().get('confidence_score', 0.0) if cdoc.exists else 0.0
            theme  = cdoc.to_dict().get('Theme/Subject', '') if cdoc.exists else ''
        except Exception:
            img = ''; conf = 0.0; theme = ''

        try:
            cdoc2  = (db.collection('users').document(d.get('user_email',''))
                        .collection('coins').document(doc.id).get())
            reviews = cdoc2.to_dict().get('grade_reviews', []) if cdoc2.exists else []
        except Exception:
            reviews = []

        grade_tally: dict = {}
        for rv in reviews:
            g = rv.get('suggested_grade', rv.get('action',''))
            if g and g != 'confirmed':
                grade_tally[g] = grade_tally.get(g, 0) + 1

        flags.append({
            'flag_id':         doc.id,
            'coin_id':         d.get('coin_id', doc.id),
            'user_email':      d.get('user_email', ''),
            'year':            d.get('year', ''),
            'mint_mark':       d.get('mint_mark', ''),
            'program_series':  d.get('program_series', ''),
            'theme_subject':   theme,
            'ai_grade':        d.get('ai_assigned_grade', ''),
            'community_grade': d.get('community_grade', ''),
            'review_count':    d.get('review_count', 0),
            'grade_tally':     grade_tally,
            'confidence_score': round(float(conf), 2),
            'image_url':       img,
            'flagged_at':      str(d.get('flagged_at', '')),
            'resolved':        d.get('resolved', False),
            'resolved_grade':  d.get('resolved_grade', ''),
            'resolved_by':     d.get('resolved_by', ''),
        })

    return {
        'status':  'ok',
        'results': flags,
        'count':   len(flags),
        'resolved': resolved,
    }

@router.post("/admin/grade_flags/{flag_id}/resolve")
async def resolve_grade_flag(
    flag_id:        str,
    admin_email:    str = Form(...),
    decision:       str = Form(...),
    resolved_grade: str = Form(''),
    notes:          str = Form(''),
):
    """Admin resolves a flagged coin grade."""
    flag_ref = db.collection('admin_grade_flags').document(flag_id)
    flag_doc = flag_ref.get()
    if not flag_doc.exists:
        raise HTTPException(status_code=404, detail="Flag not found.")

    d          = flag_doc.to_dict()
    owner      = d.get('user_email', '')
    coin_id    = d.get('coin_id', flag_id)
    ai_grade   = d.get('ai_assigned_grade', '')
    comm_grade = d.get('community_grade', '')

    final_grade = comm_grade if decision == 'accept_community' else ai_grade
    if resolved_grade:
        final_grade = resolved_grade

    if owner and coin_id:
        coin_ref = (db.collection('users').document(owner)
                      .collection('coins').document(coin_id))
        coin_ref.set({
            'Condition':           final_grade,
            'grade_review_status': 'admin_resolved',
            'admin_resolution': {
                'decision':    decision,
                'final_grade': final_grade,
                'resolved_by': admin_email,
                'notes':       notes,
            },
        }, merge=True)

    flag_ref.set({
        'resolved':      True,
        'resolved_grade': final_grade,
        'resolved_by':   admin_email,
        'resolved_at':   firestore.SERVER_TIMESTAMP,
        'resolution':    decision,
        'admin_notes':   notes,
    }, merge=True)

    action_desc = (f"Community grade '{comm_grade}' accepted"
                   if decision == 'accept_community'
                   else f"AI grade '{ai_grade}' kept")
    return {
        'status':      'ok',
        'message':     f'Resolved: {action_desc}. Coin updated to "{final_grade}".',
        'final_grade': final_grade,
    }

@router.get("/grade_review/stats")
def grade_review_stats(user_email: str):
    """Per-user grade review statistics."""
    now = _time.time()
    last_write = GRADE_WRITE_TIMESTAMPS.get(user_email, 0)
    cache_entry = GRADE_STATS_CACHE.get(user_email)

    if (now - last_write < 2.0 or (cache_entry and now - cache_entry["timestamp"] < 5.0)) and cache_entry:
        return cache_entry["stats"]

    coins_ref = db.collection('users').document(user_email).collection('coins')

    total_ai      = 0
    pending       = 0
    confirmed_ct  = 0
    flagged_ct    = 0
    reviewed_by_me = 0

    try:
        pending_agg = coins_ref.where('grade_review_status', '==', 'pending').count().get()
        total_pending = pending_agg[0][0].value if pending_agg else 0
        
        reviewed_agg = coins_ref.where('grade_review_count', '>', 0).count().get()
        reviewed_by_me = reviewed_agg[0][0].value if reviewed_agg else 0
        
        conf_agg = coins_ref.where('grade_review_status', '==', 'confirmed').count().get()
        confirmed_ct = conf_agg[0][0].value if conf_agg else 0
        
        flagged_agg = coins_ref.where('grade_review_status', '==', 'flagged_for_admin_review').count().get()
        flagged_ct = flagged_agg[0][0].value if flagged_agg else 0

        pending = total_pending
        total_ai = pending + reviewed_by_me

        stats = {
            'total_ai_graded': total_ai,
            'pending_review':  pending,
            'reviewed_by_me':  reviewed_by_me,
            'confirmed':       confirmed_ct,
            'flagged':         flagged_ct,
        }
        GRADE_STATS_CACHE[user_email] = {"stats": stats, "timestamp": now}
        return stats
    except Exception as e:
        logger.exception("Error counting grade stats via aggregate query")
        return {
            'total_ai_graded': 0,
            'pending_review':  0,
            'reviewed_by_me':  0,
            'confirmed':       0,
            'flagged':         0,
        }
