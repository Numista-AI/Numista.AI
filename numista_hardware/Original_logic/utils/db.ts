
import { openDB, DBSchema, IDBPDatabase } from 'idb';
import { Coin, WishlistItem } from '../types';

interface NumismaDB extends DBSchema {
  coins: {
    key: string;
    value: Coin;
  };
  wishlist: {
    key: string;
    value: WishlistItem;
  };
  settings: {
    key: string;
    value: any;
  };
}

const DB_NAME = 'numisma-db-v2';
const DB_VERSION = 2;

let dbPromise: Promise<IDBPDatabase<NumismaDB>> | null = null;

const getDB = () => {
  if (!dbPromise) {
    dbPromise = openDB<NumismaDB>(DB_NAME, DB_VERSION, {
      upgrade(db, oldVersion) {
        if (oldVersion < 1) {
          db.createObjectStore('coins', { keyPath: 'id' });
          db.createObjectStore('wishlist', { keyPath: 'id' });
        }
        if (oldVersion < 2) {
          db.createObjectStore('settings');
        }
      },
    });
  }
  return dbPromise;
};

export const db = {
  // --- Coin Operations ---
  async getAllCoins(): Promise<Coin[]> {
    const db = await getDB();
    return db.getAll('coins');
  },

  async addCoin(coin: Coin): Promise<string> {
    const db = await getDB();
    await db.add('coins', coin);
    return coin.id;
  },

  async putCoin(coin: Coin): Promise<string> {
    const db = await getDB();
    await db.put('coins', coin);
    return coin.id;
  },

  async deleteCoin(id: string): Promise<void> {
    const db = await getDB();
    await db.delete('coins', id);
  },

  async bulkPutCoins(coins: Coin[]): Promise<void> {
    const db = await getDB();
    const tx = db.transaction('coins', 'readwrite');
    const store = tx.objectStore('coins');
    for (const coin of coins) {
      await store.put(coin);
    }
    await tx.done;
  },

  async clearCoins(): Promise<void> {
    const db = await getDB();
    await db.clear('coins');
  },

  // --- Wishlist Operations ---
  async getAllWishlist(): Promise<WishlistItem[]> {
    const db = await getDB();
    return db.getAll('wishlist');
  },

  async putWishlistItem(item: WishlistItem): Promise<string> {
    const db = await getDB();
    await db.put('wishlist', item);
    return item.id;
  },

  async deleteWishlistItem(id: string): Promise<void> {
    const db = await getDB();
    await db.delete('wishlist', id);
  },

  async bulkPutWishlist(items: WishlistItem[]): Promise<void> {
    const db = await getDB();
    const tx = db.transaction('wishlist', 'readwrite');
    const store = tx.objectStore('wishlist');
    for (const item of items) {
      await store.put(item);
    }
    await tx.done;
  },

  async clearWishlist(): Promise<void> {
    const db = await getDB();
    await db.clear('wishlist');
  },

  // --- Settings Operations ---
  async getSetting(key: string): Promise<any> {
    const db = await getDB();
    return db.get('settings', key);
  },

  async setSetting(key: string, value: any): Promise<void> {
    const db = await getDB();
    await db.put('settings', value, key);
  }
};
