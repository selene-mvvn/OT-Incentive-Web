import pandas as pd
import io
from logic.i18n import t

def get_payroll_period(date_obj) -> str:
    """
    Calculates payroll period based on date.
    Period is from 21st of previous month to 20th of current month.
    """
    if pd.isna(date_obj):
        return ""
    try:
        import datetime
        if isinstance(date_obj, str):
            if "/" in date_obj:
                date_obj = datetime.datetime.strptime(date_obj, "%d/%m/%Y").date()
            elif "-" in date_obj:
                date_obj = pd.to_datetime(date_obj).date()

        month = date_obj.month
        year = date_obj.year
        
        if date_obj.day >= 21:
            from_date = datetime.date(year, month, 21)
            next_month = month + 1
            next_year = year
            if next_month > 12:
                next_month = 1
                next_year += 1
            to_date = datetime.date(next_year, next_month, 20)
        else:
            to_date = datetime.date(year, month, 20)
            prev_month = month - 1
            prev_year = year
            if prev_month < 1:
                prev_month = 12
                prev_year -= 1
            from_date = datetime.date(prev_year, prev_month, 21)
            
        return f"{from_date.strftime('%d/%m/%Y')} - {to_date.strftime('%d/%m/%Y')}"
    except Exception:
        return ""

def breakdown_ot_hours(date_obj, total_hours: float, holidays_list: list) -> dict:
    """
    Phân bổ số giờ OT vào các rổ hệ số tùy thuộc vào ngày thường, cuối tuần, ngày lễ.
    Tự động xếp giờ theo thứ tự ưu tiên của ngày đó (ngày thường tính từ 17h, ngày nghỉ/lễ tính từ 8h).
    """
    is_holiday = False
    date_str = date_obj.strftime("%Y-%m-%d")
    for h in holidays_list:
        h_str = h.strftime("%Y-%m-%d") if hasattr(h, 'strftime') else str(h)
        if date_str == h_str:
            is_holiday = True
            break
            
    is_weekend = date_obj.weekday() >= 5
    
    if date_obj.weekday() == 5:
        import datetime
        next_week = date_obj + datetime.timedelta(days=7)
        if next_week.month != date_obj.month:
            is_weekend = False
    
    buckets = {150: 0.0, 200: 0.0, 270: 0.0, 300: 0.0, 400: 0.0}
    rem = total_hours
    
    if is_holiday:
        # Ngày lễ: 08:00 - 17:00 (9 tiếng) -> 400%
        # 17:00 - 22:00 (5 tiếng) -> 300%
        # > 22:00 -> 400%
        h_400_1 = min(rem, 9.0)
        buckets[400] += h_400_1
        rem -= h_400_1
        
        h_300 = min(rem, 5.0)
        buckets[300] += h_300
        rem -= h_300
        
        if rem > 0:
            buckets[400] += rem
            
    elif is_weekend:
        # Cuối tuần: 08:00 - 22:00 (14 tiếng) -> 200%
        # > 22:00 -> 270%
        h_200 = min(rem, 14.0)
        buckets[200] += h_200
        rem -= h_200
        
        if rem > 0:
            buckets[270] += rem
            
    else:
        # Ngày thường: 17:00 - 22:00 (5 tiếng) -> 150%
        # > 22:00 -> 200%
        h_150 = min(rem, 5.0)
        buckets[150] += h_150
        rem -= h_150
        
        if rem > 0:
            buckets[200] += rem
            
    return buckets

def calculate_ot_pay(gross_salary: float, standard_days: float, ot_hours: float, multiplier_percent: float) -> dict:
    """
    Calculates the OT Pay and Hourly Rate.
    Hourly Rate = Gross Salary / Standard Days / 8
    OT Pay = Hourly Rate * OT Hours * (Multiplier / 100)
    """
    if standard_days == 0:
        return {"hourly_rate": 0.0, "ot_pay": 0.0}
    
    hourly_rate = gross_salary / standard_days / 8
    ot_pay = hourly_rate * ot_hours * (multiplier_percent / 100)
    
    return {
        "hourly_rate": hourly_rate,
        "ot_pay": ot_pay
    }

def export_ot_to_excel(data: list, allow_merge: bool = True, filename: str = "", is_template: bool = False, general_period: str = "") -> io.BytesIO:
    """
    Generates an Excel file matching the requested columns exactly.
    data is a list of dictionaries with the required fields.
    If allow_merge is False, no cells will be merged (except for headers).
    """
    if is_template and not data:
        # Generate 4 empty rows for the template
        for _ in range(4):
            data.append({
                "project_type": "",
                "ot_hours": "",
                "hourly_rate": ""
            })
            
    col_tinh_ot = t("Thời gian Tính OT", "OT計算期間")
    col_chi_tra = t("Thời gian Chi trả", "支払期間")
    col_loai_da = t("Loại dự án", "プロジェクト種別")
    col_ma_dh = t("Mã đơn hàng", "注文番号")
    col_ma_dh_kh = t("Mã đơn hàng khách", "客先注文番号")
    col_ten_dh = t("Tên đơn hàng", "注文名")
    col_quan_ly = t("Quản lý", "PM")
    col_nguoi = t("Người thực hiện", "担当スタッフ")
    col_ly_do = t("Lý do OT", "残業理由")
    col_ngay = t("Ngày OT", "残業日")
    col_gio = t("Số giờ OT", "残業時間")
    col_luong = t("Số lương/h (VND)", "時給 (VND)")
    col_trang_thai = t("Trạng thái", "ステータス")

    base_columns = [
        col_tinh_ot,
        col_chi_tra,
        col_loai_da,
        col_ma_dh,
        col_ma_dh_kh,
        col_ten_dh,
        col_quan_ly,
        col_nguoi,
        col_ly_do,
        col_ngay,
        col_gio,
        col_luong
    ]
    
    # Collect all dynamic multiplier columns found in data
    mult_columns = []
    for row in data:
        for key in row.keys():
            if key.endswith("%") and key not in mult_columns:
                mult_columns.append(key)
                
    # If no multipliers exist, ensure at least some default
    if not mult_columns:
        mult_columns = ["150%", "200%", "400%", "270%", "300%"]
        
    all_columns = base_columns + mult_columns + [col_trang_thai]
    
    df_list = []
    for row in data:
        row_dict = {col: "" for col in all_columns}
        
        period = str(row.get("payment_period", ""))
        short_period = period
        try:
            if " - " in period:
                # Dạng "21/05/2026 - 20/06/2026"
                end_date_str = period.split(" - ")[1].strip()
                import datetime
                dt = datetime.datetime.strptime(end_date_str, "%d/%m/%Y")
                short_period = dt.strftime("%m/%Y")
            elif "/" in period and len(period.split("/")) == 2:
                # Dạng "06/2026"
                m, y = period.split("/")
                short_period = f"{m}/{y}"
        except Exception:
            pass
                
        row_dict[col_tinh_ot] = short_period
        row_dict[col_chi_tra] = short_period
        row_dict[col_loai_da] = row.get("project_type", "N")
        row_dict[col_ma_dh] = row.get("order_id", "")
        row_dict[col_ma_dh_kh] = row.get("client_order_id", "")
        row_dict[col_ten_dh] = row.get("order_name", "")
        row_dict[col_quan_ly] = row.get("manager_name", "")
        row_dict[col_nguoi] = row.get("employee_name", "")
        row_dict[col_ly_do] = row.get("ot_reason", "")
        row_dict[col_ngay] = row.get("ot_date", "")
        row_dict[col_gio] = row.get("ot_hours", 0.0)
        row_dict[col_luong] = row.get("hourly_rate", 0.0)
        
        for col in mult_columns:
            row_dict[col] = row.get(col, "")
            
        df_list.append(row_dict)
        
    df = pd.DataFrame(df_list, columns=all_columns)
    
    # Sort data by project information (to maintain merge cells) and then chronologically by date
    df['sort_date'] = pd.to_datetime(df[col_ngay], format='%d/%m/%Y', errors='coerce')
    df = df.sort_values(by=[col_ten_dh, col_nguoi, "sort_date"]).reset_index(drop=True)
    df = df.drop(columns=['sort_date'])
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='OT_Data', startrow=5, header=False)
        
        workbook = writer.book
        worksheet = writer.sheets['OT_Data']
        
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
            'num_format': '#,##0',
            'font_name': 'Times New Roman'
        })
        
        # Write Title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 18,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Times New Roman'
        })
        if is_template:
            title_text = t("BẢNG TỔNG HỢP TĂNG CA (OT)", "残業・費用集計表 (OT)")
        elif filename:
            title_text = filename.replace(".xlsx", "").upper()
        else:
            title_text = t("BẢNG TỔNG HỢP TĂNG CA (OT) & CHI PHÍ", "残業・費用集計表 (OT)")
        worksheet.merge_range(0, 0, 0, len(all_columns) - 1, title_text, title_format)
        worksheet.set_row(0, 30)  # Make title row taller
        
        # Add payroll period as subtitle
        if general_period:
            subtitle_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'italic': True,
                'font_size': 12,
                'font_name': 'Times New Roman'
            })
            worksheet.merge_range(1, 0, 1, len(all_columns) - 1, f"{t('Kỳ tính lương', '給与計算期間')}: {general_period}", subtitle_format)
            worksheet.set_row(1, 20)
        
        # Write headers
        try:
            ot_idx = base_columns.index(col_tinh_ot)
            pay_idx = base_columns.index(col_chi_tra)
        except ValueError:
            ot_idx = pay_idx = -1
            
        for col_num, col_name in enumerate(base_columns):
            if col_num == ot_idx:
                worksheet.write(4, col_num, t("Tính OT", "OT計算"), header_format)
            elif col_num == pay_idx:
                worksheet.write(4, col_num, t("Chi trả", "支払"), header_format)
            else:
                worksheet.merge_range(3, col_num, 4, col_num, col_name, header_format)
                
        if ot_idx != -1 and pay_idx != -1 and pay_idx == ot_idx + 1:
            worksheet.merge_range(3, ot_idx, 3, pay_idx, t("Thời gian", "期間"), header_format)
            
        if mult_columns:
            start_col = len(base_columns)
            end_col = start_col + len(mult_columns) - 1
            if start_col == end_col:
                worksheet.write(3, start_col, t("Số tiền tăng ca (VND)", "残業代 (VND)"), header_format)
            else:
                worksheet.merge_range(3, start_col, 3, end_col, t("Số tiền tăng ca (VND)", "残業代 (VND)"), header_format)
            
            for i, col_name in enumerate(mult_columns):
                worksheet.write(4, start_col + i, col_name, header_format)
                    
        # Write "Trạng thái" header
        status_col = len(base_columns) + len(mult_columns)
        worksheet.merge_range(3, status_col, 4, status_col, col_trang_thai, header_format)
                
        # Determine merge columns
        merge_cols = [
            col_tinh_ot, col_chi_tra, col_loai_da, 
            col_ma_dh, col_ma_dh_kh, col_ten_dh, 
            col_quan_ly, col_nguoi, col_luong
        ] if allow_merge else []
        
        # Apply data formats and merge cells
        for col_num, col_name in enumerate(df.columns):
            is_merge_col = col_name in merge_cols
            is_money_col = (col_name == col_luong or col_name in mult_columns)
            
            if is_merge_col:
                start_row = 0
                while start_row < len(df):
                    val = df.iloc[start_row, col_num]
                    order_name = df.iloc[start_row, df.columns.get_loc(col_ten_dh)]
                    employee = df.iloc[start_row, df.columns.get_loc(col_nguoi)]
                    
                    end_row = start_row
                    while end_row + 1 < len(df):
                        next_val = df.iloc[end_row + 1, col_num]
                        next_order_name = df.iloc[end_row + 1, df.columns.get_loc(col_ten_dh)]
                        next_employee = df.iloc[end_row + 1, df.columns.get_loc(col_nguoi)]
                        if next_val == val and next_order_name == order_name and next_employee == employee and str(order_name).strip() != "" and str(order_name).strip().lower() != "nan":
                            end_row += 1
                        else:
                            break
                        
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
                        
                    if end_row > start_row:
                        worksheet.merge_range(start_row + 5, col_num, end_row + 5, col_num, display_val, cell_format)
                    else:
                        worksheet.write(start_row + 5, col_num, display_val, cell_format)
                        
                    start_row = end_row + 1
            else:
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
                        
                    worksheet.write(row_num + 5, col_num, display_val, cell_format)
                
        # Auto-fit columns
        def get_str_width(s):
            lines = str(s).split('\n')
            if not lines: return 0
            # Use 2.0 for Japanese (CJK) characters (> 0x2E80)
            # Use 1.1 for Latin/Vietnamese characters
            return max(sum(2.0 if ord(c) > 0x2E80 else 1.1 for c in line) for line in lines)
            
        for col_num, col_name in enumerate(df.columns):
            is_money_col = (col_name == col_luong or col_name in mult_columns)
            
            header_len = get_str_width(col_name)
            if col_name == col_tinh_ot:
                header_len = get_str_width(t("Tính OT", "OT計算"))
            elif col_name == col_chi_tra:
                header_len = get_str_width(t("Chi trả", "支払"))
                
            max_len = header_len
            
            for row_num in range(len(df)):
                val = df.iloc[row_num, col_num]
                
                if pd.isna(val) or str(val).strip() == "" or str(val).strip() == "nan":
                    str_for_len = ""
                elif is_money_col:
                    try:
                        str_for_len = f"{round(float(val)):,}"
                    except ValueError:
                        str_for_len = str(val)
                else:
                    str_for_len = str(val)
                    
                cell_len = get_str_width(str_for_len)
                if cell_len > max_len:
                    max_len = cell_len
            
            # Additional safety clamp to ensure columns don't stretch excessively
            if col_name in [col_tinh_ot, col_chi_tra]:
                max_len = min(max_len, 12)
            elif col_name == col_ly_do:
                max_len = min(max_len, 45) # Cap the reason column so it doesn't get ridiculously wide
                
            if is_template:
                # Narrower columns for time, hours, and money to prevent them from being too wide
                if col_name in [col_tinh_ot, col_chi_tra, col_gio, col_luong] or col_name in mult_columns:
                    max_len = max(max_len, 11)
                else:
                    max_len = max(max_len, 16)
                
            worksheet.set_column(col_num, col_num, max_len + 2)
            
    buffer.seek(0)
    return buffer
