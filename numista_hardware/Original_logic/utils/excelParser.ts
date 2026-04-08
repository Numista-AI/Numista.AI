
import * as XLSX from 'xlsx';
import { Coin } from '../types';

export const parseExcelFile = async (file: File): Promise<any[]> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = e.target?.result;
        const workbook = XLSX.read(data, { type: 'binary' });
        const targetSheetName = workbook.SheetNames.find(name => name.toUpperCase().includes("COINS")) || workbook.SheetNames[0];
        const sheet = workbook.Sheets[targetSheetName];
        const jsonData = XLSX.utils.sheet_to_json(sheet);
        resolve(jsonData);
      } catch (error) { reject(error); }
    };
    reader.onerror = (error) => reject(error);
    reader.readAsBinaryString(file);
  });
};

export const exportCollectionToExcel = (coins: Coin[]) => {
  const data = coins.map(coin => ({
    "Country": coin.country,
    "Year": coin.year,
    "Mint Mark": coin.mintMark || '',
    "Denomination": coin.denomination,
    "Quantity": coin.quantity,
    "Program/Series": coin.series || '',
    "Theme/Subject": coin.theme || '',
    "Condition": coin.condition,
    "Surface & Strike Quality": coin.surfaceQuality || '',
    "Grading Service": coin.certification?.service || '',
    "Grading Certification Number": coin.certification?.serialNumber || '',
    "Cost": coin.purchaseCost || 0,
    "Purchase Date": coin.datePurchased || '',
    "Retailer/Website": coin.retailer || '',
    "Retailer Item No.": coin.retailerItemNo || '',
    "Retailer Invoice #": coin.retailerInvoiceNo || '',
    "Metal Content": coin.metalContent || '',
    "Melt Value": coin.meltValue || 0,
    "Personal Notes": coin.personalNotes || '',
    "Personal Reference #": coin.personalRefNo || '',
    "Storage Location": coin.storageLocation || '',
    "Variety (Legacy)": coin.varietyLegacy || '',
    "Notes (Legacy)": coin.notesLegacy || ''
  }));

  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "My Collection");
  XLSX.writeFile(wb, `Numisma_Export_${new Date().toISOString().split('T')[0]}.xlsx`);
};

export const downloadExcelTemplate = () => {
  const templateData = [{
    "Country": "USA",
    "Year": "1964",
    "Mint Mark": "P",
    "Denomination": "Quarter",
    "Quantity": 1,
    "Program/Series": "Washington Quarters",
    "Theme/Subject": "Silver",
    "Condition": "MS-65",
    "Surface & Strike Quality": "Sharp, full luster",
    "Grading Service": "PCGS",
    "Grading Certification Number": "12345678",
    "Cost": 25.00,
    "Purchase Date": "15 JAN 2024",
    "Retailer/Website": "Local Coin Shop",
    "Retailer Item No.": "1413.6",
    "Retailer Invoice #": "JS050119",
    "Metal Content": "90% Silver",
    "Melt Value": 5.40,
    "Personal Notes": "Example entry",
    "Personal Reference #": "REF-001",
    "Storage Location": "Safe Deposit Box A",
    "Variety (Legacy)": "N/A",
    "Notes (Legacy)": "Standard Silver Quarter"
  }];

  const ws = XLSX.utils.json_to_sheet(templateData);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Enter Coins");
  
  // Set column widths for better UX
  const wscols = Array(23).fill({ wch: 20 });
  ws['!cols'] = wscols;

  XLSX.writeFile(wb, "Numisma_Import_Template.xlsx");
};
