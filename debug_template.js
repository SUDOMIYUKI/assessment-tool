const ExcelJS = require('exceljs');
const path = require('path');

async function debugTemplate() {
    console.log('🔍 テンプレート詳細診断開始');
    
    try {
        const templatePath = path.join(__dirname, 'templates/アセスメントシート原本.xlsx');
        console.log('📋 テンプレートパス:', templatePath);
        
        // ファイルの存在確認
        const fs = require('fs');
        if (!fs.existsSync(templatePath)) {
            console.error('❌ テンプレートファイルが存在しません');
            return;
        }
        
        const stats = fs.statSync(templatePath);
        console.log('📁 ファイル情報:');
        console.log('- サイズ:', stats.size, 'bytes');
        console.log('- 作成日:', stats.birthtime);
        console.log('- 更新日:', stats.mtime);
        
        // ExcelJSで読み込み
        const workbook = new ExcelJS.Workbook();
        console.log('📖 ExcelJSで読み込み中...');
        
        await workbook.xlsx.readFile(templatePath);
        
        console.log('📊 ワークブック情報:');
        console.log('- シート数:', workbook.worksheets.length);
        
        workbook.worksheets.forEach((ws, index) => {
            console.log(`  ${index + 1}. ${ws.name}`);
            console.log(`     - 行数: ${ws.rowCount}`);
            console.log(`     - 列数: ${ws.columnCount}`);
            console.log(`     - 結合セル数: ${ws.model.merges ? ws.model.merges.length : 0}`);
            
            // 実際に使用されている範囲を確認
            const usedRange = ws.dimensions;
            if (usedRange) {
                console.log(`     - 使用範囲: ${usedRange.top}行${usedRange.left}列 - ${usedRange.bottom}行${usedRange.right}列`);
            }
        });
        
        // メインシートを取得
        let mainSheet = workbook.getWorksheet('ｱｾｽﾒﾝﾄｼｰﾄ');
        if (!mainSheet) {
            mainSheet = workbook.worksheets[0];
            console.log('⚠️ アセスメントシートが見つからないため、最初のシートを使用:', mainSheet.name);
        }
        
        // セルの実際の内容を確認
        console.log('🔍 セルの内容確認:');
        const testCells = ['D3', 'H3', 'P3', 'B11', 'B18'];
        testCells.forEach(cellRef => {
            const cell = mainSheet.getCell(cellRef);
            console.log(`  ${cellRef}:`);
            console.log(`    - 値: "${cell.value}"`);
            console.log(`    - 数式: "${cell.formula}"`);
            console.log(`    - 書式: ${JSON.stringify(cell.style, null, 2)}`);
        });
        
        // 結合セルの詳細確認
        if (mainSheet.model.merges && mainSheet.model.merges.length > 0) {
            console.log('🔗 結合セルの詳細:');
            mainSheet.model.merges.forEach((merge, index) => {
                console.log(`  ${index + 1}: ${merge.top}行${merge.left}列 - ${merge.bottom}行${merge.right}列`);
                // 結合セル内の内容を確認
                const cell = mainSheet.getCell(merge.top, merge.left);
                console.log(`     値: "${cell.value}"`);
            });
        }
        
        // 行と列の書式を確認
        console.log('📏 行・列の書式確認:');
        for (let row = 1; row <= 20; row++) {
            const rowHeight = mainSheet.getRow(row).height;
            if (rowHeight) {
                console.log(`  行${row}の高さ: ${rowHeight}`);
            }
        }
        
        for (let col = 1; col <= 20; col++) {
            const colWidth = mainSheet.getColumn(col).width;
            if (colWidth) {
                console.log(`  列${col}の幅: ${colWidth}`);
            }
        }
        
        console.log('✅ 診断完了');
        
    } catch (error) {
        console.error('❌ エラー:', error);
        console.error('スタックトレース:', error.stack);
    }
}

debugTemplate();
