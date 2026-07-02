import pandas as pd
import io
from logic.i18n import t

def calculate_incentive(target_hours: float, actual_hours: float, unit_price: float, company_charge: float) -> dict:
    """
    Calculates Profit, Standard Incentive, and Final Incentive based on input.
    """
    profit = (target_hours * unit_price) - (actual_hours * company_charge)
    standard_incentive = (unit_price - company_charge) * 0.3
    final_incentive = (target_hours - actual_hours) * standard_incentive
    
    return {
        "profit": profit,
        "standard_incentive": standard_incentive,
        "final_incentive": final_incentive
    }

def generate_incentive_excel(data: list, title: str = None) -> io.BytesIO:
    
    if not data:
        return None
        
    col_ngay = t("Ngày ghi nhận", "記録日")
    col_du_an = t("Tên dự án", "案件名")
    col_nguoi = t("Người thực hiện", "担当者")
    col_kh = t("Giờ công KH", "目標工数")
    col_tt = t("Giờ công TT", "実工数")
    col_gia = t("Đơn giá", "単価")
    col_charge = t("Company Charge", "会社運用ﾁｬｰｼﾞ")
    col_loi_nhuan = t("Lợi nhuận", "利益")
    col_in_tc = t("Incentive TC", "基準金額")
    col_nhan = t("Nhận được", "受取額")
    col_ghi_chu = t("Ghi chú", "備考")
    
    columns = [
        col_ngay, col_du_an, col_nguoi,
        col_kh, col_tt, col_gia, col_charge,
        col_loi_nhuan, col_in_tc, col_nhan, col_ghi_chu
    ]
    
    df_list = []
    for row in data:
        df_list.append({
            col_ngay: row.get("date", ""),
            col_du_an: row.get("project_name", ""),
            col_nguoi: row.get("employee_name", ""),
            col_kh: row.get("target_hours", 0),
            col_tt: row.get("actual_hours", 0),
            col_gia: row.get("unit_price", 0),
            col_charge: row.get("company_charge", 0),
            col_loi_nhuan: row.get("profit", 0),
            col_in_tc: row.get("standard_incentive", 0),
            col_nhan: row.get("final_incentive", 0),
            col_ghi_chu: row.get("notes", "")
        })
        
    df = pd.DataFrame(df_list, columns=columns)
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Incentive_Data', startrow=4, header=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Incentive_Data']
        
        header_format = workbook.add_format({
            'bg_color': 'black',
            'font_color': 'white',
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_name': 'Times New Roman'
        })
        
        data_format = workbook.add_format({
            'bg_color': '#D9D9D9',
            'font_color': 'black',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Times New Roman'
        })
        
        money_format = workbook.add_format({
            'bg_color': '#D9D9D9',
            'font_color': 'black',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '"¥" #,##0',
            'font_name': 'Times New Roman'
        })
        
        # Write Title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Times New Roman'
        })
        if title is None:
            title = t("BẢNG TỔNG HỢP INCENTIVE", "インセンティブ集計表")
        worksheet.merge_range(0, 0, 0, len(columns) - 1, title, title_format)
        worksheet.set_row(0, 30)
        
        # Write headers
        worksheet.set_row(3, 30) # make header row tall enough for 2 lines
        for col_num, col_name in enumerate(columns):
            worksheet.write(3, col_num, col_name, header_format)
            
        # Apply data formats
        for col_num, col_name in enumerate(df.columns):
            is_money_col = col_name in [col_gia, col_charge, col_loi_nhuan, col_in_tc, col_nhan]
            
            for row_num in range(len(df)):
                val = df.iloc[row_num, col_num]
                cell_format = money_format if is_money_col else data_format
                
                if pd.isna(val) or str(val).strip() == "" or str(val).strip() == "nan":
                    display_val = ""
                elif is_money_col:
                    try:
                        display_val = round(float(val))
                    except ValueError:
                        display_val = val
                else:
                    display_val = val
                    
                worksheet.write(row_num + 4, col_num, display_val, cell_format)
                
        # Auto-fit columns
        def get_str_width(s):
            lines = str(s).split('\n')
            if not lines: return 0
            return max(sum(2.2 if ord(c) > 127 else 1.2 for c in line) for line in lines)
            
        for col_num, col_name in enumerate(df.columns):
            is_money_col = col_name in [col_gia, col_charge, col_loi_nhuan, col_in_tc, col_nhan]
            
            # calculate width by taking max length among lines
            max_len = max(get_str_width(line) for line in str(col_name).split('\n'))
            
            for row_num in range(len(df)):
                val = df.iloc[row_num, col_num]
                
                if pd.isna(val) or str(val).strip() == "" or str(val).strip() == "nan":
                    str_for_len = ""
                elif is_money_col:
                    try:
                        str_for_len = f"¥ {round(float(val)):,}"
                    except ValueError:
                        str_for_len = str(val)
                else:
                    str_for_len = str(val)
                    
                cell_len = max(get_str_width(line) for line in str_for_len.split('\n'))
                if cell_len > max_len:
                    max_len = cell_len
                    
            worksheet.set_column(col_num, col_num, max_len + 2)
            
    buffer.seek(0)
    return buffer
