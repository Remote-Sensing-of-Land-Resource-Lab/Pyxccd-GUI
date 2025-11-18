import matplotlib
matplotlib.use('TkAgg')  
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os
import ctypes
from textwrap import dedent
os.environ['GDAL_DATA'] = r'D:\py3.11.9\Lib\site-packages\rasterio\gdal-data'

class ChangeDetectionApp:
    def __init__(self, root):
        self.root = root
        
        # 初始化字体和DPI设置
        self.init_fonts()
        self.set_dpi_awareness()
        self.last_params = {}
        self.root.title("Pyxccd GUI1.0")
        self.root.geometry("900x930")  
        
        # 存储数据
        self.df = None
        self.available_columns = []
        self.selected_columns = {
            'date': None,
            'qa': None,
            'bands': [],
            'display_band': None,
            'break_indicator': None
        }
        
        # 设置样式
        self.style = ttk.Style()
        self.configure_styles()
        
        self.create_widgets()
    
    def init_fonts(self):
        """初始化字体设置"""
        # 主字体设置
        self.main_font = ('Microsoft YaHei', 10)  # Windows系统字体
        self.title_font = ('Microsoft YaHei', 11, 'bold')
        self.mono_font = ('Courier New', 10)  # 等宽字体用于代码显示
        
        # 设置全局默认字体
        self.root.option_add('*Font', self.main_font)
    
    def set_dpi_awareness(self):
        """设置DPI感知以提高清晰度"""
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    
    def configure_styles(self):
        """配置所有样式"""
        # 基础样式
        self.style.configure('.', font=self.main_font)
        
        # 定义板块背景颜色
        self.section_colors = {
            'input': '#F0F8FF',    # AliceBlue
            'band': '#F5FFFA',    # Cornsilk
            'method': '#FFF8DC',  # MintCream
            'param': '#F0FFF0',   # Honeydew
            'display': '#F5F5F5'  # WhiteSmoke
        }
        
        # 特定控件样式
        self.style.configure('TFrame', background='white')
        self.style.configure('TLabel', background='white')
        self.style.configure('Title.TLabel', font=self.title_font)
        self.style.configure('TButton', padding=5)
        self.style.configure('TEntry', padding=5)
        self.style.configure('TCombobox', padding=5)
        
        # 列表框样式
        self.style.configure('Listbox', font=self.main_font)
        
        # 复选框样式
        self.style.configure('TCheckbutton', font=self.main_font)
        
        # 单选框样式
        self.style.configure('TRadiobutton', font=self.main_font)
        
        # 添加Method区域控件的样式
        self.style.configure('Method.TRadiobutton', 
                           background=self.section_colors['method'])
        self.style.configure('Method.TLabel', 
                           background=self.section_colors['method'])
        
        # 自定义板块样式
        self.style.configure('Input.TFrame', background=self.section_colors['input'])
        self.style.configure('Band.TFrame', background=self.section_colors['band'])
        self.style.configure('Method.TFrame', background=self.section_colors['method'])
        self.style.configure('Param.TFrame', background=self.section_colors['param'])
        self.style.configure('Display.TFrame', background=self.section_colors['display'])
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ==================== Input区域 ====================
        input_frame = ttk.Frame(main_frame, style='Input.TFrame', padding=10, relief=tk.RIDGE, borderwidth=2)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_label = ttk.Label(input_frame, text="Input (CSV or Excel)", style='Title.TLabel')
        input_label.pack(anchor=tk.W, pady=(0, 5))
        
        input_subframe = ttk.Frame(input_frame)
        input_subframe.pack(fill=tk.X)
        
        self.input_var = tk.StringVar()
        entry = ttk.Entry(input_subframe, textvariable=self.input_var, width=60)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        open_btn = ttk.Button(input_subframe, text="Open", command=self.open_file)
        open_btn.pack(side=tk.RIGHT)
        
        # ==================== Band selection区域 ====================
        band_frame = ttk.Frame(main_frame, style='Band.TFrame', padding=10, relief=tk.RIDGE, borderwidth=2)
        band_frame.pack(fill=tk.X, pady=(0, 10))
        
        band_label = ttk.Label(band_frame, text="Band selection for break detection", style='Title.TLabel')
        band_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 第二行：列选择区域
        selection_frame = ttk.Frame(band_frame)
        selection_frame.pack(fill=tk.X)
        
        # 左侧：可用列列表（带边框）
        available_frame = ttk.LabelFrame(selection_frame, text="Available columns", padding=5)
        available_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(available_frame, text="Double-click to add band:(only support integer)").pack(anchor=tk.W)
        self.available_listbox = tk.Listbox(
            available_frame, 
            height=8, 
            width=20, 
            borderwidth=1, 
            relief="solid",
            font=self.main_font
        )
        self.available_listbox.pack(fill=tk.BOTH, expand=True)
        self.available_listbox.bind('<Double-Button-1>', self.on_available_double_click)
        
        # 右侧：选择区域
        right_frame = ttk.Frame(selection_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Date选择
        date_frame = ttk.Frame(right_frame)
        date_frame.pack(fill=tk.X, pady=2)
        ttk.Label(date_frame, text="Date column:", width=15).pack(side=tk.LEFT)
        self.date_var = tk.StringVar()
        self.date_combo = ttk.Combobox(date_frame, textvariable=self.date_var, width=25, state="readonly")
        self.date_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        self.date_combo.bind('<<ComboboxSelected>>', self.on_date_selected)

        # QA选择
        qa_frame = ttk.Frame(right_frame)
        qa_frame.pack(fill=tk.X, pady=2)

        self.qa_enable_var = tk.BooleanVar(value=False)
        qa_check = ttk.Checkbutton(
            qa_frame, 
            text="QA column:", 
            variable=self.qa_enable_var, 
            command=self.toggle_qa_selection
        )
        qa_check.pack(side=tk.LEFT)

        # 添加一个等宽的空标签来对齐
        ttk.Label(qa_frame, width=2).pack(side=tk.LEFT)

        self.qa_var = tk.StringVar()
        self.qa_combo = ttk.Combobox(
            qa_frame, 
            textvariable=self.qa_var, 
            width=25, 
            state="readonly"
        )
        self.qa_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        self.qa_combo.config(state="disabled")  # 默认禁用
        self.qa_combo.bind('<<ComboboxSelected>>', self.on_qa_selected)
        
        # 波段选择（多选）- 带边框
        bands_frame = ttk.LabelFrame(right_frame, text="Selected bands", padding=5)
        bands_frame.pack(fill=tk.BOTH, expand=True, pady=2)
        
        ttk.Label(bands_frame, text="Double-click to remove:").pack(anchor=tk.W)
        
        self.bands_listbox = tk.Listbox(
            bands_frame, 
            height=8, 
            selectmode=tk.SINGLE, 
            borderwidth=1, 
            relief="solid",
            font=self.main_font
        )
        self.bands_listbox.pack(fill=tk.BOTH, expand=True)
        self.bands_listbox.bind('<Double-Button-1>', self.on_selected_band_double_click)
        
        # 添加break indicator band选择框
        break_indicator_frame = ttk.Frame(right_frame)
        break_indicator_frame.pack(fill=tk.X, pady=2)

        ttk.Label(break_indicator_frame, text="Break indicator band:", width=20).pack(side=tk.LEFT)
        self.break_indicator_var = tk.StringVar()
        self.break_indicator_combo = ttk.Combobox(
            break_indicator_frame, 
            textvariable=self.break_indicator_var, 
            width=25, 
            state="readonly"
        )
        self.break_indicator_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        self.break_indicator_combo.bind('<<ComboboxSelected>>', self.on_break_indicator_selected)
        
        # ==================== Method选择区域 ====================
        method_frame = ttk.Frame(main_frame, style='Method.TFrame', padding=10, relief=tk.RIDGE, borderwidth=2)
        method_frame.pack(fill=tk.X, pady=(0, 10))
        
        method_label = ttk.Label(method_frame, text="Method", style='Title.TLabel')
        method_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 创建方法选择的容器框架
        method_options_frame = ttk.Frame(method_frame, style='Method.TFrame')
        method_options_frame.pack(fill=tk.X)
        
        # 创建一个内部框架来放置单选按钮
        inner_frame = ttk.Frame(method_options_frame, style='Method.TFrame')
        inner_frame.pack(side=tk.LEFT)  # 左对齐，不填满
        
        self.method_var = tk.StringVar(value="S-CCD")  # 默认选择S-CCD
        
        # 先添加S-CCD选项
        sccd_rb = ttk.Radiobutton(
            method_options_frame, 
            text="S-CCD", 
            variable=self.method_var, 
            value="S-CCD",
            style='Method.TRadiobutton'
        )
        sccd_rb.pack(side=tk.LEFT)
        
        # 添加间距（约40像素），并设置正确的背景色
        spacer = ttk.Label(
            method_options_frame, 
            width=10, 
            style='Method.TLabel'  # 使用Method样式的Label
        )
        spacer.pack(side=tk.LEFT)
        
        # 然后添加COLD选项
        cold_rb = ttk.Radiobutton(
            method_options_frame, 
            text="COLD", 
            variable=self.method_var, 
            value="COLD",
            style='Method.TRadiobutton'  # 使用Method样式的RadioButton
        )
        cold_rb.pack(side=tk.LEFT)
        
        # 添加一个填充框架确保右边空白区域也有正确背景色
        filler = ttk.Frame(method_options_frame, style='Method.TFrame')
        filler.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # 添加方法选择回调
        self.method_var.trace_add('write', self.on_method_changed)
        
        # ==================== Parameter区域 ====================
        param_frame = ttk.Frame(main_frame, style='Param.TFrame', padding=10, relief=tk.RIDGE, borderwidth=2)
        param_frame.pack(fill=tk.X, pady=(0, 10))
        
        param_label = ttk.Label(param_frame, text="Parameter", style='Title.TLabel')
        param_label.pack(anchor=tk.W, pady=(0, 5))
        
        param_subframe = ttk.Frame(param_frame)
        param_subframe.pack(fill=tk.X)
        
        # 左侧参数
        left_param_frame = ttk.Frame(param_subframe)
        left_param_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.p_cg_var = tk.StringVar(value="0.99")
        self.conse_var = tk.StringVar(value="6")
        self.lam_var = tk.StringVar(value="20")
        
        self.create_param_row(left_param_frame, "P_CG:", self.p_cg_var)
        self.create_param_row(left_param_frame, "CONSE:", self.conse_var)
        self.lam_entry = self.create_param_row(left_param_frame, "Lam:", self.lam_var)
        
        # 右侧参数
        right_param_frame = ttk.Frame(param_subframe)
        right_param_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        self.trimodal_var = tk.BooleanVar(value=True)
        
        self.trimodal_check = self.create_checkbox_row(right_param_frame, "Trimodal:", self.trimodal_var)
        self.fitting_curve_frame = self.create_fitting_curve_row(right_param_frame)
        
        # ==================== Display区域 ====================
        display_frame = ttk.Frame(main_frame, style='Display.TFrame', padding=10, relief=tk.RIDGE, borderwidth=2)
        display_frame.pack(fill=tk.X, pady=(0, 10))

        display_label = ttk.Label(display_frame, text="Display", style='Title.TLabel')
        display_label.pack(anchor=tk.W, pady=(0, 5))

        display_subframe = ttk.Frame(display_frame)
        display_subframe.pack(fill=tk.X)

        # 左侧：Display band选择
        left_display_frame = ttk.Frame(display_subframe)
        left_display_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        display_band_frame = ttk.Frame(left_display_frame)
        display_band_frame.pack(fill=tk.X, pady=2)

        ttk.Label(display_band_frame, text="Display band:", width=15).pack(side=tk.LEFT)
        self.display_band_var = tk.StringVar()
        self.display_band_combo = ttk.Combobox(
            display_band_frame, 
            textvariable=self.display_band_var, 
            width=15, 
            state="readonly"
        )
        self.display_band_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.display_band_combo.bind('<<ComboboxSelected>>', self.on_display_band_selected)

        # 右侧：Output选项和View Script按钮
        right_display_frame = ttk.Frame(display_subframe)
        right_display_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Output选项
        output_frame = ttk.Frame(right_display_frame)
        output_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        ttk.Label(output_frame, text="Output:", width=10).pack(side=tk.LEFT)
        self.output_var = tk.StringVar(value="breaks")  # 默认选择breaks
        self.output_combo = ttk.Combobox(
            output_frame, 
            textvariable=self.output_var, 
            values=["breaks", "state_components", "anomaly"], 
            state="readonly", 
            width=20
        )
        self.output_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.output_combo.bind('<<ComboboxSelected>>', self.on_output_changed)  # 添加绑定事件
    
        # View Script按钮
        view_script_button = ttk.Button(
            right_display_frame, 
            text="View Script", 
            command=lambda: self.show_script(self.last_params)
        )
        view_script_button.pack(side=tk.RIGHT)

        # 初始禁用S-CCD特有选项
        self.on_method_changed()
        
        # ==================== Run按钮 ====================
        run_frame = ttk.Frame(main_frame)
        run_frame.pack(fill=tk.X, pady=10)

        # 左侧填充框架（用于居中Run按钮）
        left_filler = ttk.Frame(run_frame)
        left_filler.pack(side=tk.LEFT, expand=True)

        # Run按钮（居中）
        run_button = ttk.Button(
            run_frame, 
            text="Run", 
            command=self.run_analysis
        )
        run_button.pack(side=tk.LEFT)

        # 中间填充框架（在Run和Help之间）
        middle_filler = ttk.Frame(run_frame)
        middle_filler.pack(side=tk.LEFT, expand=True)

        # Help按钮（靠右）
        help_button = ttk.Button(
            run_frame, 
            text="Help", 
            command=self.show_help
        )
        help_button.pack(side=tk.RIGHT)
    
    
    
    def create_param_row(self, parent, label, var):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        ttk.Label(frame, text=label, width=20).pack(side=tk.LEFT)
        entry = ttk.Entry(frame, textvariable=var, width=10)
        entry.pack(side=tk.LEFT)
        return entry
    
    def create_checkbox_row(self, parent, label, var):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        check = ttk.Checkbutton(
            frame, 
            text=label, 
            variable=var, 
            command=lambda: self.update_checkbox_label(frame, var)
        )
        check.pack(side=tk.LEFT)
        # 显示当前状态
        state_label = "yes" if var.get() else "no"
        ttk.Label(frame, text=state_label).pack(side=tk.LEFT, padx=5)
        return check
    
    def create_fitting_curve_row(self, parent):
        """Create the Fitting curve selection row with three options on the next line"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        
        # First row: Label
        label_frame = ttk.Frame(frame)
        label_frame.pack(fill=tk.X)
        ttk.Label(label_frame, text="Fitting curve:", width=20).pack(side=tk.LEFT)
        
        # Second row: Radio buttons with indentation
        self.radio_frame = ttk.Frame(frame)  # Make it an instance variable for later access
        self.radio_frame.pack(fill=tk.X, padx=(0, 0))  # Add left padding for indentation
        
        # Create the radio buttons
        self.fitting_curve_var = tk.StringVar(value="Lasso")
        
        self.lasso_rb = ttk.Radiobutton(
            self.radio_frame, 
            text="Lasso regression", 
            variable=self.fitting_curve_var, 
            value="Lasso"
        )
        self.lasso_rb.pack(side=tk.LEFT)
        
        self.kalman_rb = ttk.Radiobutton(
            self.radio_frame, 
            text="Kalman Filter", 
            variable=self.fitting_curve_var, 
            value="Kalman"
        )
        self.kalman_rb.pack(side=tk.LEFT, padx=10)
        
        self.states_rb = ttk.Radiobutton(
            self.radio_frame, 
            text="States", 
            variable=self.fitting_curve_var, 
            value="States"
        )
        self.states_rb.pack(side=tk.LEFT)
        
        return frame
    
    def on_output_changed(self, event):
        """当Output选项变化时的回调函数"""
        selected_output = self.output_var.get()
        
        if selected_output == "state_components":
            # 锁定Fitting curve为States
            self.fitting_curve_var.set("States")
            self.lasso_rb.config(state="disabled")
            self.kalman_rb.config(state="disabled")
            self.states_rb.config(state="disabled")
        else:
            # 恢复Fitting curve的可选状态（根据当前方法）
            method = self.method_var.get()
            if method == "S-CCD":
                self.lasso_rb.config(state="normal")
                self.kalman_rb.config(state="normal")
                self.states_rb.config(state="normal")
    
    def on_method_changed(self, *args):
        """当方法选择改变时的回调函数"""
        method = self.method_var.get()
        if method == "S-CCD":
            # 启用S-CCD特有选项
            self.trimodal_check.config(state="normal")
            # 启用Fitting curve选项
            self.lasso_rb.config(state="normal")
            self.kalman_rb.config(state="normal")
            self.states_rb.config(state="normal")
            # 启用Output选择
            self.output_combo.config(state="readonly")
        else:
            # 禁用S-CCD特有选项
            self.trimodal_check.config(state="disabled")
            # 禁用Fitting curve选项
            self.lasso_rb.config(state="disabled")
            self.kalman_rb.config(state="disabled")
            self.states_rb.config(state="disabled")
            # 禁用Output选择并设置为breaks
            self.output_var.set("breaks")
            self.output_combo.config(state="disabled")  # 禁用Output选择框
    
    def update_checkbox_label(self, frame, var):
        """更新复选框后的标签"""
        for widget in frame.winfo_children():
            if isinstance(widget, ttk.Label) and widget.cget('text') in ['yes', 'no']:
                widget.config(text="yes" if var.get() else "no")
                break
    
    def open_file(self):
        filetypes = [
            ('数据文件', '*.csv *.xlsx *.xls'),
            ('CSV文件', '*.csv'),
            ('Excel文件', '*.xlsx *.xls')
        ]
        
        filename = filedialog.askopenfilename(title='打开数据文件', filetypes=filetypes)
        
        if filename:
            self.input_var.set(filename)
            try:
                if filename.endswith('.csv'):
                    self.df = pd.read_csv(filename)
                else:
                    self.df = pd.read_excel(filename)
                
                self.available_columns = self.df.columns.tolist()
                # 清空所有选择
                self.clear_all_selections()
                self.update_column_lists()
                
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败: {str(e)}")
    
    def clear_all_selections(self):
        """清空所有选择（包括日期、QA和波段）"""
        # 清空波段相关选项
        self.selected_columns['bands'] = []
        self.selected_columns['display_band'] = None
        self.selected_columns['break_indicator'] = None
        self.bands_listbox.delete(0, tk.END)
        self.display_band_var.set('')
        self.break_indicator_var.set('')
        
        # 清空日期和QA选择
        self.selected_columns['date'] = None
        self.date_var.set('')
        
        self.selected_columns['qa'] = None
        self.qa_var.set('')
        self.qa_enable_var.set(False)
        self.qa_combo.config(state="disabled")
    
        # 清空下拉框选项
        self.display_band_combo['values'] = []
        self.break_indicator_combo['values'] = []
    
    def update_column_lists(self):
        """更新所有列选择列表"""
        # 更新可用列列表
        self.available_listbox.delete(0, tk.END)
        for col in self.available_columns:
            self.available_listbox.insert(tk.END, col)
        
        # 更新下拉选择框
        self.date_combo['values'] = self.available_columns
        self.qa_combo['values'] = self.available_columns
        
        # 更新显示波段下拉框，只显示已选波段
        self.update_display_band_combo()
        
        # 更新已选波段列表
        self.bands_listbox.delete(0, tk.END)
        for band in self.selected_columns['bands']:
            self.bands_listbox.insert(tk.END, band)
    
    def update_display_band_combo(self):
        """更新显示波段下拉框，只显示已选波段，并自动选择第一个波段"""
        # 更新下拉框选项
        self.display_band_combo['values'] = self.selected_columns['bands']
        self.break_indicator_combo['values'] = self.selected_columns['bands']
        
        # 验证当前选择的波段是否仍然有效
        if (self.selected_columns['display_band'] and 
            self.selected_columns['display_band'] not in self.selected_columns['bands']):
            self.selected_columns['display_band'] = None
            self.display_band_var.set('')
        
        if (self.selected_columns['break_indicator'] and 
            self.selected_columns['break_indicator'] not in self.selected_columns['bands']):
            self.selected_columns['break_indicator'] = None
            self.break_indicator_var.set('')
        
        # 自动选择逻辑
        if self.selected_columns['bands']:
            first_band = self.selected_columns['bands'][0]
            
            # 自动设置break indicator band
            if not self.selected_columns['break_indicator']:
                self.break_indicator_var.set(first_band)
                self.selected_columns['break_indicator'] = first_band
            
            # 自动设置display band
            if not self.selected_columns['display_band']:
                self.display_band_var.set(first_band)
                self.selected_columns['display_band'] = first_band
        
    def on_date_selected(self, event):
        """日期列选择事件"""
        selected_date = self.date_var.get()
        if selected_date and selected_date in self.available_columns:
            self.selected_columns['date'] = selected_date
    
    def on_qa_selected(self, event):
        """QA列选择事件"""
        if self.qa_enable_var.get():  # 只有在QA启用时才更新
            selected_qa = self.qa_var.get()
            if selected_qa and selected_qa in self.available_columns:
                self.selected_columns['qa'] = selected_qa
            else:
                self.selected_columns['qa'] = None
    
    def on_display_band_selected(self, event):
        """显示波段选择事件"""
        selected_band = self.display_band_var.get()
        if selected_band and selected_band in self.selected_columns['bands']:
            self.selected_columns['display_band'] = selected_band
    
    def toggle_qa_selection(self):
        """切换QA选择框状态"""
        if self.qa_enable_var.get():
            self.qa_combo.config(state="readonly")
            # 如果已经有选中的QA列，更新selected_columns
            if self.qa_var.get() in self.available_columns:
                self.selected_columns['qa'] = self.qa_var.get()
        else:
            self.qa_combo.config(state="disabled")
            self.qa_var.set('')
            self.selected_columns['qa'] = None
    
    def on_available_double_click(self, event):
        """双击添加波段"""
        selection = self.available_listbox.curselection()
        if selection:
            band = self.available_listbox.get(selection[0])
            if (band not in self.selected_columns['bands'] and 
                band != self.selected_columns['date'] and 
                band != self.selected_columns['qa']):
                self.selected_columns['bands'].append(band)
                self.bands_listbox.insert(tk.END, band)
                # 如果是第一个添加的波段，自动设置为display band和break indicator band
                if len(self.selected_columns['bands']) == 1:
                    self.display_band_var.set(band)
                    self.selected_columns['display_band'] = band
                    self.break_indicator_var.set(band)
                    self.selected_columns['break_indicator'] = band
                else:
                    # 更新下拉框选项
                    self.update_display_band_combo()
    
    def on_selected_band_double_click(self, event):
        """双击移除波段"""
        selection = self.bands_listbox.curselection()
        if selection:
            band = self.bands_listbox.get(selection[0])
            if band in self.selected_columns['bands']:
                # 检查是否要移除当前选择的display band或break indicator band
                is_display_band = self.selected_columns['display_band'] == band
                is_break_indicator = self.selected_columns['break_indicator'] == band
                
                self.selected_columns['bands'].remove(band)
                self.bands_listbox.delete(selection[0])
                
                # 如果移除的波段是当前选择的display band，则重新选择第一个波段
                if is_display_band:
                    if self.selected_columns['bands']:
                        new_display_band = self.selected_columns['bands'][0]
                        self.display_band_var.set(new_display_band)
                        self.selected_columns['display_band'] = new_display_band
                    else:
                        self.display_band_var.set('')
                        self.selected_columns['display_band'] = None
                
                # 如果移除的波段是当前选择的break indicator band，则重新选择第一个波段
                if is_break_indicator:
                    if self.selected_columns['bands']:
                        new_break_indicator = self.selected_columns['bands'][0]
                        self.break_indicator_var.set(new_break_indicator)
                        self.selected_columns['break_indicator'] = new_break_indicator
                    else:
                        self.break_indicator_var.set('')
                        self.selected_columns['break_indicator'] = None
                
                # 更新下拉框选项
                self.update_display_band_combo()

    def on_break_indicator_selected(self, event):
        """break indicator band选择事件"""
        selected_band = self.break_indicator_var.get()
        if selected_band and selected_band in self.selected_columns['bands']:
            self.selected_columns['break_indicator'] = selected_band
    
    def show_help(self):
        """显示帮助信息"""
        help_text = dedent(f"""This software was designed to quickly test and visualize signle time-series results for the python package "pyxccd".

    Version Information:
    - Version: 1.0
    - Release Date: 2025-11-11

    Author Information:
    - Correspondence: Dr. Su Ye, su.ye@zju.edu.cn
    - Main Developer: Yingchu Hu
    - Institution: Institute of Agricultural Remote Sensing and Information Technology Application, College of Environmental and Resource Sciences, Zhejiang University

    Software Features:
    - S-CCD/COLD Change Detection Algorithm
    - state-space time-eries decomposition
    - Break-aware curve fitting
    - Supports CSV and Excel Data Input
    - Visualizes break, state and curve fitting 

    Usage Instructions:
    1. Select input data file (CSV or Excel format)
    2. Configure band selection parameters
    3. Choose detection method (S-CCD or COLD)
    4. Set relevant parameters
    5. Click Run to start analysis

    Technical Support:
    For any issues, please contact: su.ye@zju.edu.cn
        """)
        
        # 创建帮助窗口
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Pyxccd GUI")
        help_window.geometry("500x400")
        help_window.resizable(True, True)
        
        # 设置窗口图标（如果有的话）
        # help_window.iconbitmap("icon.ico")
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(help_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=60,
            height=20,
            font=self.main_font
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 插入帮助文本
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)  # 设置为只读
        
        # 添加关闭按钮
        close_button = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy
        )
        close_button.pack(pady=10)
        
        # 使窗口居中
        self.center_window(help_window)

    def center_window(self, window):
        """使窗口居中显示"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_script(self, params=None):
        """显示固定的脚本内容，可选包含参数"""
        """运行分析"""
        # 验证输入
        if self.df is None:
            messagebox.showerror("Error", "Please select a data file first")
            return
        
        if not self.selected_columns['date']:
            messagebox.showerror("Error", "Please select the date column")
            return
        
        if not self.selected_columns['display_band']:
            messagebox.showerror("Error", "Please select the display band column")
            return
        
        if not self.selected_columns['bands']:
            messagebox.showerror("Error", "Please select at least one band")
            return
        
        if not self.selected_columns['qa'] and self.qa_enable_var.get():
            messagebox.showerror("Error", "Please select the QA column")
            return
        
        try:
            p_cg = float(self.p_cg_var.get())
            if not (0.0 < p_cg < 1.0):  # P_CG 应该是 (0.0, 1.0] 范围内的浮点数
                messagebox.showerror("Error", "P_CG must be a float in the range (0.0, 1.0]")
                return
        except ValueError:
            messagebox.showerror("Error", "P_CG must be a valid float number")
            return

        # 验证 CONSE 参数
        try:
            conse = int(self.conse_var.get())
            if not (0 < conse <= 8):  # CONSE 应该是 (0, 8] 范围内的整数
                messagebox.showerror("Error", "CONSE must be an integer in the range (0, 8]")
                return
        except ValueError:
            messagebox.showerror("Error", "CONSE must be a valid integer")
            return
        
        # 获取output选项
        output_option = self.output_var.get()
        
        # 收集参数
        params = {
            'input_file': self.input_var.get(),
            'method': self.method_var.get(),
            'date_column': self.selected_columns['date'],
            'qa_column': self.selected_columns['qa'],
            'selected_bands': self.selected_columns['bands'],
            'break_indicator': self.selected_columns['break_indicator'],
            'display_band': self.selected_columns['display_band'],
            'P_CG': self.p_cg_var.get(),
            'CONSE': self.conse_var.get(),
            'output': output_option,  # 使用新的output参数
            'Lam': self.lam_var.get(),
            'trimodal': self.trimodal_var.get(),
            'fitting_curve': self.fitting_curve_var.get(),
        }
        # 保存参数以便在show_script中使用
        self.last_params = params
        
        
        
        script_window = tk.Toplevel(self.root)
        script_window.title("Script Content")
        script_window.geometry("800x600")
        
        text_area = scrolledtext.ScrolledText(
            script_window, 
            wrap=tk.WORD, 
            width=100, 
            height=30,
            font=self.mono_font
        )
        text_area.pack(fill=tk.BOTH, expand=True)
        try:
            header_content = """import matplotlib
matplotlib.use('TkAgg')  
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import ctypes
from textwrap import dedent
import numpy as np
import os
from pyxccd import cold_detect_flex,sccd_detect_flex
from pyxccd.common import cold_rec_cg
from pyxccd.utils import read_data, getcategory_cold
from datetime import date
from typing import List, Tuple, Dict, Union, Optional
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pyxccd.common import SccdOutput, anomaly
from pyxccd.utils import getcategory_sccd, defaults, getcategory_cold, predict_ref
from matplotlib.lines import Line2D   
from tkinter import messagebox
def check_and_convert_dates(dates):
    
    try:
        dates = np.array(dates) if not isinstance(dates, np.ndarray) else dates

        if len(dates) == 0:
            messagebox.showerror("Error", "Date data is empty")
            return None
        
        # Check the type and range of each element
        for i, date in enumerate(dates):
            if isinstance(date, (int, float, np.integer, np.floating)):
                if not (700000 <= date <= 800000):  
                    messagebox.showerror("Error", f"Date value is out of reasonable range(700000-800000): {date}")
                    return None
            
            # Processing string-type dates
            elif isinstance(date, str):
                try:
                    pd.to_datetime(date, format='%m/%d/%Y')
                except ValueError:
                    try:
                        pd.to_datetime(date)
                    except ValueError:
                        messagebox.showerror("Error", f"Date format error: {date}")
                        return None
            else:
                messagebox.showerror("Error", f"Unsupported date format: {date}")
                return None
            
        # If all dates are in string format, perform the conversion
        if isinstance(dates[0], str):
            try:
                dates = pd.to_datetime(dates, format='%m/%d/%Y')
                dates = dates.to_series().apply(lambda x: x.toordinal()).values

                if not np.all((700000 <= dates) & (dates <= 800000)):
                    invalid_dates = dates[(dates < 700000) | (dates > 800000)]
                    messagebox.showerror("Error", 
                        f"The converted date is out of range(700000-800000): {invalid_dates[:5]}...")
                    return None
            except Exception as e:
                messagebox.showerror("Error", f"Date conversion failed:{str(e)}")
                return None

        return np.array(dates, dtype=np.int64) if not isinstance(dates, np.ndarray) else dates.astype(np.int64)
    
    except Exception as e:
        messagebox.showerror("Error", f"Error occurred while processing date: {str(e)}")
        return None
    
def display_sccd_result_sif(
    data: np.ndarray,
    band_names: List[str],
    band_index: int,
    indicator_band_index: int,
    sccd_result: SccdOutput,
    axe: Axes,
    title: str = 'S-CCD',
    states: Optional[pd.DataFrame] = None,
    anomaly: Optional[anomaly] = None,
    trimodal: Optional[bool] = False, 
    plot_kwargs: Optional[Dict] = None
) -> Tuple[plt.Figure, List[plt.Axes]]:
    
    w = np.pi * 2 / 365.25

    # Set default plot parameters
    default_plot_kwargs: Dict[str, Union[int, float, str]] = {
        'marker_size': 5,
        'marker_alpha': 0.7,
        'line_color': 'orange',
        'font_size': 14
    }
    if plot_kwargs is not None:
        default_plot_kwargs.update(plot_kwargs)

    # Extract values with proper type casting
    font_size = default_plot_kwargs.get('font_size', 14)
    try:
        title_font_size = int(font_size) + 2
    except (TypeError, ValueError):
        title_font_size = 16 

    # Clean and prepare data
    data = data[np.all(np.isfinite(data), axis=1)]
    data_df = pd.DataFrame(data, columns=['dates'] + band_names + ['qa'])

    # Plot COLD results
    w = np.pi * 2 / 365.25
    slope_scale = 10000

    # Prepare clean data for COLD plot
    data_clean = data_df[(data_df['qa'] == 0) | (data_df['qa'] == 1)].copy()
    data_clean = data_clean[(data_clean >= 0).all(axis=1) & (data_clean.drop(columns="dates") <= 10000).all(axis=1)]
    calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in data_clean["dates"]]
    data_clean.loc[:, 'dates_formal'] = calendar_dates
    
    # Calculate y-axis limits
    band_name = band_names[band_index]
    band_values = data_clean[data_clean['qa'] == 0 | (data_clean['qa'] == 1)][band_name]
    q01, q99 = np.quantile(band_values, [0.01, 0.99])
    extra = (q99 - q01) * 0.4
    ylim_low = q01 - extra
    ylim_high = q99 + extra

    # Plot SCCD observations
    axe.plot(
        'dates_formal', band_name, 'go',
        markersize=default_plot_kwargs['marker_size'],
        alpha=default_plot_kwargs['marker_alpha'],
        data=data_clean
    )

    # Plot SCCD segments - NEW: use states if provided
    if states is not None:
        # Build column names based on band_index
        col_prefix = f"b{band_index}"
        trend_col = f"{col_prefix}_trend"
        annual_col = f"{col_prefix}_annual"
        semiannual_col = f"{col_prefix}_semiannual"
        trimodal_col = f"{col_prefix}_trimodal"
        
        # Check required columns exist
        required_cols = [trend_col, annual_col, semiannual_col]
        missing_cols = [col for col in required_cols if col not in states.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in states: {missing_cols}")
        
        # Convert dates
        states["dates_formal"] = [pd.Timestamp.fromordinal(int(row)) for row in states["dates"]]
        
        # Calculate combined prediction (General)
        has_trimodal = trimodal_col in states.columns
        if has_trimodal:
            states["General"] = states[trend_col] + states[annual_col] + states[semiannual_col] + states[trimodal_col]
        else:
            states["General"] = states[trend_col] + states[annual_col] + states[semiannual_col]
        
        # Plot fitted curve
        g = sns.lineplot(
            x="dates_formal", y="General",
            data=states,
            label="Model fit",
            ax=axe,
            color=default_plot_kwargs['line_color']
        )
        if g.legend_ is not None: 
            g.legend_.remove()
    else:
        # Original segment-by-segment plotting
        for segment in sccd_result.rec_cg:
            j = np.arange(segment['t_start'], segment['t_break'] + 1, 1)
            
            if trimodal:  
                plot_df = pd.DataFrame(
                    {
                    'dates': j,
                    'trend': j * segment['coefs'][band_index][1] / slope_scale + segment['coefs'][band_index][0],
                    'annual': np.cos(w * j) * segment['coefs'][band_index][2] + np.sin(w * j) * segment['coefs'][band_index][3],
                    'semiannual': np.cos(2 * w * j) * segment['coefs'][band_index][4] + np.sin(2 * w * j) * segment['coefs'][band_index][5],
                    'trimodal': np.cos(3 * w * j) * segment['coefs'][band_index][6] + np.sin(3 * w * j) * segment['coefs'][band_index][7]
                })
            else:  
                plot_df = pd.DataFrame(
                    {
                    'dates': j,
                    'trend': j * segment['coefs'][band_index][1] / slope_scale + segment['coefs'][band_index][0],
                    'annual': np.cos(w * j) * segment['coefs'][band_index][2] + np.sin(w * j) * segment['coefs'][band_index][3],
                    'semiannual': np.cos(2 * w * j) * segment['coefs'][band_index][4] + np.sin(2 * w * j) * segment['coefs'][band_index][5],
                    'trimodal': j * 0
                })
                
            plot_df['predicted'] = (
                plot_df['trend'] + 
                plot_df['annual'] + 
                plot_df['semiannual'] +
                plot_df['trimodal']
            )

            # Convert dates and plot model fit
            calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in plot_df["dates"]]
            plot_df.loc[:, 'dates_formal'] = calendar_dates
            g = sns.lineplot(
                x="dates_formal", y="predicted",
                data=plot_df,
                label="Model fit",
                ax=axe,
                color=default_plot_kwargs['line_color']
            )
            if g.legend_ is not None: 
                g.legend_.remove()

        # Plot near-real-time projection for SCCD if available
        if hasattr(sccd_result, 'nrt_mode') and (sccd_result.nrt_mode %10 == 1 or sccd_result.nrt_mode == 3 or sccd_result.nrt_mode %10 == 5):
            recent_obs = sccd_result.nrt_model['obs_date_since1982'][sccd_result.nrt_model['obs_date_since1982']>0]
            j = np.arange(
                sccd_result.nrt_model['t_start_since1982'].item() + defaults['COMMON']['JULIAN_LANDSAT4_LAUNCH'], 
                recent_obs[-1].item()+ defaults['COMMON']['JULIAN_LANDSAT4_LAUNCH']+1, 
                1
            )

            if trimodal: 
                plot_df = pd.DataFrame(
                    {
                    'dates': j,
                    'trend': j * sccd_result.nrt_model['nrt_coefs'][band_index][1] / slope_scale + sccd_result.nrt_model['nrt_coefs'][band_index][0],
                    'annual': np.cos(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][2] + np.sin(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][3],
                    'semiannual': np.cos(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][4] + np.sin(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][5],
                    'trimodal': np.cos(3 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][6] + np.sin(3 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][7]
                })
            else:
                plot_df = pd.DataFrame(
                    {
                    'dates': j,
                    'trend': j * sccd_result.nrt_model['nrt_coefs'][band_index][1] / slope_scale + sccd_result.nrt_model['nrt_coefs'][band_index][0],
                    'annual': np.cos(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][2] + np.sin(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][3],
                    'semiannual': np.cos(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][4] + np.sin(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][5],
                    'trimodal': j * 0
                })
                
            plot_df['predicted'] = plot_df['trend'] + plot_df['annual'] + plot_df['semiannual'] + plot_df['trimodal']
            calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in plot_df["dates"]]
            plot_df.loc[:, 'dates_formal'] = calendar_dates
            g = sns.lineplot(
                x="dates_formal", y="predicted",
                data=plot_df,
                label="Model fit",
                ax=axe,
                color=default_plot_kwargs['line_color']
            )
            if g.legend_ is not None: 
                g.legend_.remove()
                        
    # add manual legends
    if anomaly is not None:
        legend_elements = [Line2D([0], [0], label=f'{band_names[indicator_band_index]} decrease break', color='k'),
                            Line2D([0], [0], label=f'{band_names[indicator_band_index]} increase break', color='r'),
                            Line2D([0], [0], marker='o', color="#EAEAF2",
                            markerfacecolor="#EAEAF2", markeredgecolor="black",
                            label=f'{band_names[indicator_band_index]} decrease anomalies', lw=0, markersize=8),
                            Line2D([0], [0], marker='o', color="#EAEAF2",
                            markerfacecolor="#EAEAF2", markeredgecolor="red",
                            label=f'{band_names[indicator_band_index]} increase anomalies', lw=0, markersize=8)]
    else:
        legend_elements = [Line2D([0], [0], label=f'{band_names[indicator_band_index]} decrease break', color='k'),
                        Line2D([0], [0], label=f'{band_names[indicator_band_index]} increase break', color='r')]
    axe.legend(handles=legend_elements, loc='upper left', prop={'size': 9})
    
    # plot breaks
    for i in range(len(sccd_result.rec_cg)):
        if sccd_result.rec_cg[i]['magnitude'][indicator_band_index] < 0:    
            axe.axvline(pd.Timestamp.fromordinal(sccd_result.rec_cg[i]['t_break']), color='k')
        else:
            axe.axvline(pd.Timestamp.fromordinal(sccd_result.rec_cg[i]['t_break']), color='r')
    
    # plot anomalies if available
    if anomaly is not None:
        n_coefs = 8 if trimodal else 6
        
        for i in range(len(anomaly.rec_cg_anomaly)):
            pred_ref = np.asarray(
                    [
                        predict_ref(
                            anomaly.rec_cg_anomaly[i]["coefs"][0],
                            anomaly.rec_cg_anomaly[i]["obs_date_since1982"][i_conse].item()
                            + defaults['COMMON']['JULIAN_LANDSAT4_LAUNCH'], num_coefficients=n_coefs
                        ) for i_conse in range(3)
                    ]
            )

            cm = anomaly.rec_cg_anomaly[i]["obs"][0, 0: 3] - pred_ref
            
            if np.median(cm) > 0:
                yc = data[data[:,0] == anomaly.rec_cg_anomaly[i]['t_break']][0][1]
                axe.plot(pd.Timestamp.fromordinal(anomaly.rec_cg_anomaly[i]['t_break']), yc,'ro',fillstyle='none',markersize=8)         
            else:
                yc = data[data[:,0] == anomaly.rec_cg_anomaly[i]['t_break']][0][1]
                axe.plot(pd.Timestamp.fromordinal(anomaly.rec_cg_anomaly[i]['t_break']), yc,'ko',fillstyle='none',markersize=8) 
    
    axe.set_ylabel(f"{band_name} * 10000", fontsize=default_plot_kwargs['font_size'])

    # Handle tick params with type safety
    tick_font_size = default_plot_kwargs['font_size']
    if isinstance(tick_font_size, (int, float)):
        axe.tick_params(axis='x', labelsize=int(tick_font_size)-1)
    else:
        axe.tick_params(axis='x', labelsize=13)  # fallback

    axe.set(ylim=(ylim_low, ylim_high))
    axe.set_xlabel("", fontsize=6)

    # Format spines
    for spine in axe.spines.values():
        spine.set_edgecolor('black')
    title_font_size = int(font_size) + 2 if isinstance(font_size, (int, float)) else 16
    axe.set_title(title, fontweight="bold", size=title_font_size, pad=2)
    

def display_cold_result(
    data: np.ndarray,
    band_names: List[str],
    band_index: int,
    indicator_band_index: int,
    cold_result: cold_rec_cg,
    axe: Axes,
    title: str = 'COLD',
    plot_kwargs: Optional[Dict] = None
) -> Tuple[plt.Figure, List[plt.Axes]]:
    
    w = np.pi * 2 / 365.25

    # Set default plot parameters
    default_plot_kwargs: Dict[str, Union[int, float, str]] = {
        'marker_size': 5,
        'marker_alpha': 0.7,
        'line_color': 'orange',
        'font_size': 14
    }
    if plot_kwargs is not None:
        default_plot_kwargs.update(plot_kwargs)

    # Extract values with proper type casting
    font_size = default_plot_kwargs.get('font_size', 14)
    try:
        title_font_size = int(font_size) + 2
    except (TypeError, ValueError):
        title_font_size = 16 


    # Clean and prepare data
    data = data[np.all(np.isfinite(data), axis=1)]
    data_df = pd.DataFrame(data, columns=['dates'] + band_names + ['qa'])

    # Plot COLD results
    w = np.pi * 2 / 365.25
    slope_scale = 10000

    # Prepare clean data for COLD plot
    data_clean = data_df[(data_df['qa'] == 0) | (data_df['qa'] == 1)].copy()
    data_clean =  data_clean[(data_clean >= 0).all(axis=1) & (data_clean.drop(columns="dates") <= 10000).all(axis=1)]
    calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in data_clean["dates"]]
    data_clean.loc[:, 'dates_formal'] = calendar_dates
    
    # Calculate y-axis limits
    band_name = band_names[band_index]
    band_values = data_clean[data_clean['qa'] == 0][band_name]
    q01, q99 = np.quantile(band_values, [0.01, 0.99])
    extra = (q99 - q01) * 0.4
    ylim_low = q01 - extra
    ylim_high = q99 + extra

    # Plot COLD observations
    axe.plot(
        'dates_formal', band_name, 'go',
        markersize=default_plot_kwargs['marker_size'],
        alpha=default_plot_kwargs['marker_alpha'],
        data=data_clean
    )

    # Plot COLD segments
    for segment in cold_result:
        j = np.arange(segment['t_start'], segment['t_end'] + 1, 1)
        plot_df = pd.DataFrame({
            'dates': j,
            'trend': j * segment['coefs'][band_index][1] / slope_scale + segment['coefs'][band_index][0],
            'annual': np.cos(w * j) * segment['coefs'][band_index][2] + np.sin(w * j) * segment['coefs'][band_index][3],
            'semiannual': np.cos(2 * w * j) * segment['coefs'][band_index][4] + np.sin(2 * w * j) * segment['coefs'][band_index][5],
            'trimodel': np.cos(3 * w * j) * segment['coefs'][band_index][6] + np.sin(3 * w * j) * segment['coefs'][band_index ][7]
        })
        plot_df['predicted'] = (
            plot_df['trend'] + 
            plot_df['annual'] + 
            plot_df['semiannual'] + 
            plot_df['trimodel']
        )

        # Convert dates and plot model fit
        calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in plot_df["dates"]]
        plot_df.loc[:, 'dates_formal'] = calendar_dates
        g = sns.lineplot(
            x="dates_formal", y="predicted",
            data=plot_df,
            label="Model fit",
            ax=axe,
            color=default_plot_kwargs['line_color']
        )
        if g.legend_ is not None: 
            g.legend_.remove()

    # add manual legends
    legend_elements = [Line2D([0], [0], label=f'{band_names[indicator_band_index]} decrease break', color='k'),
                    Line2D([0], [0], label=f'{band_names[indicator_band_index]} increase break', color='r')]
    axe.legend(handles=legend_elements, loc='upper left', prop={'size': 9})
    
    # plot breaks
    for i in range(len(cold_result)):
        if  cold_result[i]['change_prob'] == 100:
            if cold_result[i]['magnitude'][indicator_band_index] < 0:
                axe.axvline(pd.Timestamp.fromordinal(cold_result[i]['t_break']), color='k')
            else:
                axe.axvline(pd.Timestamp.fromordinal(cold_result[i]['t_break']), color='r')
    
    axe.set_ylabel(f"{band_name} * 10000", fontsize=default_plot_kwargs['font_size'])

    # Handle tick params with type safety
    tick_font_size = default_plot_kwargs['font_size']
    if isinstance(tick_font_size, (int, float)):
        axe.tick_params(axis='x', labelsize=int(tick_font_size)-1)
    else:
        axe.tick_params(axis='x', labelsize=13)  # fallback

    axe.set(ylim=(ylim_low, ylim_high))
    axe.set_xlabel("", fontsize=6)

    # Format spines
    for spine in axe.spines.values():
        spine.set_edgecolor('black')
    title_font_size = int(font_size) + 2 if isinstance(font_size, (int, float)) else 16
    axe.set_title(title, fontweight="bold", size=title_font_size, pad=2)

def display_sccd_result(
    data: np.ndarray,
    band_names: List[str],
    band_index: int,
    indicator_band_index: int,
    sccd_result: SccdOutput,
    axe: Axes,
    title: str = 'S-CCD',
    states: Optional[pd.DataFrame] = None,
    plot_kwargs: Optional[Dict] = None
) -> Tuple[plt.Figure, List[plt.Axes]]:
    
    w = np.pi * 2 / 365.25

    # Set default plot parameters
    default_plot_kwargs: Dict[str, Union[int, float, str]] = {
        'marker_size': 5,
        'marker_alpha': 0.7,
        'line_color': 'orange',
        'font_size': 14
    }
    if plot_kwargs is not None:
        default_plot_kwargs.update(plot_kwargs)

    # Extract values with proper type casting
    font_size = default_plot_kwargs.get('font_size', 14)
    try:
        title_font_size = int(font_size) + 2
    except (TypeError, ValueError):
        title_font_size = 16 

    # Clean and prepare data
    data = data[np.all(np.isfinite(data), axis=1)]
    data_df = pd.DataFrame(data, columns=['dates'] + band_names + ['qa'])

    # Plot COLD results
    w = np.pi * 2 / 365.25
    slope_scale = 10000

    # Prepare clean data for COLD plot
    data_clean = data_df[(data_df['qa'] == 0) | (data_df['qa'] == 1)].copy()
    data_clean = data_clean[(data_clean >= 0).all(axis=1) & (data_clean.drop(columns="dates") <= 10000).all(axis=1)]
    calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in data_clean["dates"]]
    data_clean.loc[:, 'dates_formal'] = calendar_dates
    
    # Calculate y-axis limits
    band_name = band_names[band_index]
    band_values = data_clean[data_clean['qa'] == 0 | (data_clean['qa'] == 1)][band_name]
    q01, q99 = np.quantile(band_values, [0.01, 0.99])
    extra = (q99 - q01) * 0.4
    ylim_low = q01 - extra
    ylim_high = q99 + extra

    # Plot SCCD observations
    axe.plot(
        'dates_formal', band_name, 'go',
        markersize=default_plot_kwargs['marker_size'],
        alpha=default_plot_kwargs['marker_alpha'],
        data=data_clean
    )

    # Plot SCCD segments - NEW: use states if provided
    if states is not None:
        # Build column names based on band_index
        col_prefix = f"b{band_index}"
        trend_col = f"{col_prefix}_trend"
        annual_col = f"{col_prefix}_annual"
        semiannual_col = f"{col_prefix}_semiannual"
        trimodal_col = f"{col_prefix}_trimodal"
        
        # Check required columns exist
        required_cols = [trend_col, annual_col, semiannual_col]
        missing_cols = [col for col in required_cols if col not in states.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in states: {missing_cols}")
        
        # Convert dates
        states["dates_formal"] = [pd.Timestamp.fromordinal(int(row)) for row in states["dates"]]
        
        # Calculate combined prediction (General)
        has_trimodal = trimodal_col in states.columns
        if has_trimodal:
            states["General"] = states[trend_col] + states[annual_col] + states[semiannual_col] + states[trimodal_col]
        else:
            states["General"] = states[trend_col] + states[annual_col] + states[semiannual_col]
        
        # Plot fitted curve
        g = sns.lineplot(
            x="dates_formal", y="General",
            data=states,
            label="Model fit",
            ax=axe,
            color=default_plot_kwargs['line_color']
        )
        if g.legend_ is not None: 
            g.legend_.remove()
    else:
        # Original segment-by-segment plotting
        for segment in sccd_result.rec_cg:
            j = np.arange(segment['t_start'], segment['t_break'] + 1, 1)
            if len(segment['coefs'][band_index]) == 8:
                plot_df = pd.DataFrame(
                    {
                    'dates': j,
                    'trend': j * segment['coefs'][band_index][1] / slope_scale + segment['coefs'][band_index][0],
                    'annual': np.cos(w * j) * segment['coefs'][band_index][2] + np.sin(w * j) * segment['coefs'][band_index][3],
                    'semiannual': np.cos(2 * w * j) * segment['coefs'][band_index][4] + np.sin(2 * w * j) * segment['coefs'][band_index][5],
                    'trimodal': np.cos(3 * w * j) * segment['coefs'][band_index][6] + np.sin(3 * w * j) * segment['coefs'][band_index][7]
                })
            else:
                plot_df = pd.DataFrame(
                    {
                    'dates': j,
                    'trend': j * segment['coefs'][band_index][1] / slope_scale + segment['coefs'][band_index][0],
                    'annual': np.cos(w * j) * segment['coefs'][band_index][2] + np.sin(w * j) * segment['coefs'][band_index][3],
                    'semiannual': np.cos(2 * w * j) * segment['coefs'][band_index][4] + np.sin(2 * w * j) * segment['coefs'][band_index][5],
                    'trimodal': j * 0
                })
            plot_df['predicted'] = (
                plot_df['trend'] + 
                plot_df['annual'] + 
                plot_df['semiannual'] +
                plot_df['trimodal']
            )

            # Convert dates and plot model fit
            calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in plot_df["dates"]]
            plot_df.loc[:, 'dates_formal'] = calendar_dates
            g = sns.lineplot(
                x="dates_formal", y="predicted",
                data=plot_df,
                label="Model fit",
                ax=axe,
                color=default_plot_kwargs['line_color']
            )
            if g.legend_ is not None: 
                g.legend_.remove()

    # Plot near-real-time projection for SCCD if available
    if hasattr(sccd_result, 'nrt_mode') and (sccd_result.nrt_mode %10 == 1 or sccd_result.nrt_mode == 3 or sccd_result.nrt_mode %10 == 5):
        recent_obs = sccd_result.nrt_model['obs_date_since1982'][sccd_result.nrt_model['obs_date_since1982']>0]
        j = np.arange(
            sccd_result.nrt_model['t_start_since1982'].item() + defaults['COMMON']['JULIAN_LANDSAT4_LAUNCH'], 
            recent_obs[-1].item()+ defaults['COMMON']['JULIAN_LANDSAT4_LAUNCH']+1, 
            1
        )

        if len(sccd_result.nrt_model['nrt_coefs'][band_index]) == 8:
            plot_df = pd.DataFrame(
                {
                'dates': j,
                'trend': j * sccd_result.nrt_model['nrt_coefs'][band_index][1] / slope_scale + sccd_result.nrt_model['nrt_coefs'][band_index][0],
                'annual': np.cos(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][2] + np.sin(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][3],
                'semiannual': np.cos(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][4] + np.sin(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][5],
                'trimodal': np.cos(3 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][6] + np.sin(3 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][7]
            })
        else:
            plot_df = pd.DataFrame(
                {
                'dates': j,
                'trend': j * sccd_result.nrt_model['nrt_coefs'][band_index][1] / slope_scale + sccd_result.nrt_model['nrt_coefs'][band_index][0],
                'annual': np.cos(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][2] + np.sin(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][3],
                'semiannual': np.cos(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][4] + np.sin(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][5],
                'trimodal': j * 0
            })
            
        plot_df['predicted'] = plot_df['trend'] + plot_df['annual'] + plot_df['semiannual'] + plot_df['trimodal']
        calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in plot_df["dates"]]
        plot_df.loc[:, 'dates_formal'] = calendar_dates
        g = sns.lineplot(
            x="dates_formal", y="predicted",
            data=plot_df,
            label="Model fit",
            ax=axe,
            color=default_plot_kwargs['line_color']
        )
        if g.legend_ is not None: 
            g.legend_.remove()

    # add manual legends
    legend_elements = [Line2D([0], [0], label=f'{band_names[indicator_band_index]} decrease break', color='k'),
                    Line2D([0], [0], label=f'{band_names[indicator_band_index]} increase break', color='r')]
    axe.legend(handles=legend_elements, loc='upper left', prop={'size': 9})
    
    # plot breaks
    for i in range(len(sccd_result.rec_cg)):
        if sccd_result.rec_cg[i]['magnitude'][indicator_band_index] < 0:
            axe.axvline(pd.Timestamp.fromordinal(sccd_result.rec_cg[i]['t_break']), color='k')
        else:
            axe.axvline(pd.Timestamp.fromordinal(sccd_result.rec_cg[i]['t_break']), color='r')
    
    axe.set_ylabel(f"{band_name} * 10000", fontsize=default_plot_kwargs['font_size'])

    # Handle tick params with type safety
    tick_font_size = default_plot_kwargs['font_size']
    if isinstance(tick_font_size, (int, float)):
        axe.tick_params(axis='x', labelsize=int(tick_font_size)-1)
    else:
        axe.tick_params(axis='x', labelsize=13)  # fallback

    axe.set(ylim=(ylim_low, ylim_high))
    axe.set_xlabel("", fontsize=6)

    # Format spines
    for spine in axe.spines.values():
        spine.set_edgecolor('black')
    title_font_size = int(font_size) + 2 if isinstance(font_size, (int, float)) else 16
    axe.set_title(title, fontweight="bold", size=title_font_size, pad=2)

def display_sccd_states_flex(
    data_df: pd.DataFrame,
    states: pd.DataFrame,
    axes: Axes,
    variable_name: str,
    title: str,
    band_name: str,
    band_index: int,  
    plot_kwargs: Optional[Dict] = None
):
    
    default_plot_kwargs = {
        'marker_size': 5,
        'marker_alpha': 0.7,
        'line_color': 'orange',
        'font_size': 14
    }
    if plot_kwargs is not None:
        default_plot_kwargs.update(plot_kwargs)

    col_prefix = f"b{band_index}"  
    
    trend_col = f"{col_prefix}_trend"
    annual_col = f"{col_prefix}_annual"
    semiannual_col = f"{col_prefix}_semiannual"
    trimodal_col = f"{col_prefix}_trimodal"  
    
    # Verify if the column exists (trimodal optional)
    required_cols = [trend_col, annual_col, semiannual_col]
    missing_cols = [col for col in required_cols if col not in states.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}. Available columns: {states.columns.tolist()}")

    has_trimodal = trimodal_col in states.columns  

    states["dates_formal"] = [pd.Timestamp.fromordinal(int(row)) for row in states["dates"]]

    # Plot the trend component (1st subplot)
    extra = (np.max(states[trend_col]) - np.min(states[trend_col])) / 4
    axes[0].set(ylim=(np.min(states[trend_col]) - extra, np.max(states[trend_col]) + extra))
    sns.lineplot(x="dates_formal", y=trend_col, data=states, ax=axes[0], color="orange")
    axes[0].set(ylabel="Trend")

    # Plot the annual cycle component (second subplot)
    extra = (np.max(states[annual_col]) - np.min(states[annual_col])) / 4
    axes[1].set(ylim=(np.min(states[annual_col]) - extra, np.max(states[annual_col]) + extra))
    sns.lineplot(x="dates_formal", y=annual_col, data=states, ax=axes[1], color="orange")
    axes[1].set(ylabel="Annual cycle")

    # Plot the semi-annual cycle component (the 3rd subplot)
    extra = (np.max(states[semiannual_col]) - np.min(states[semiannual_col])) / 4
    axes[2].set(ylim=(np.min(states[semiannual_col]) - extra, np.max(states[semiannual_col]) + extra))
    sns.lineplot(x="dates_formal", y=semiannual_col, data=states, ax=axes[2], color="orange")
    axes[2].set(ylabel="Semi-annual cycle")

    current_ax_index = 3  # Current subgraph index

    # If there is a trimodal column, plot the trimodal component (the 4th subplot)
    if has_trimodal:
        extra = (np.max(states[trimodal_col]) - np.min(states[trimodal_col])) / 4
        axes[3].set(ylim=(np.min(states[trimodal_col]) - extra, np.max(states[trimodal_col]) + extra))
        sns.lineplot(x="dates_formal", y=trimodal_col, data=states, ax=axes[3], color="orange")
        axes[3].set(ylabel="Trimodal cycle")
        current_ax_index += 1  # If a trimodal is plotted, the next subplot index is incremented by 1.

    # Plot raw data (subplot current_ax_index)
    data_clean = data_df[(data_df["qa"] == 0) | (data_df['qa'] == 1)].copy()
    data_clean["dates"] = check_and_convert_dates(data_clean["dates"])
    data_clean["dates_formal"] = [pd.Timestamp.fromordinal(int(row)) for row in data_clean["dates"]]
    axes[current_ax_index].plot(
        'dates_formal', variable_name, 'go',
        markersize=default_plot_kwargs['marker_size'],
        alpha=default_plot_kwargs['marker_alpha'],
        data=data_clean
    )

    # Plotting the fitting results (subplot current_ax_index)
    if has_trimodal:
        states["General"] = states[annual_col] + states[trend_col] + states[semiannual_col] + states[trimodal_col]
    else:
        states["General"] = states[annual_col] + states[trend_col] + states[semiannual_col]
    
    sns.lineplot(x="dates_formal", y="General", data=states, label="fit", ax=axes[current_ax_index], color="orange")
    
    band_values = data_df[data_df['qa'] == 0][variable_name]
    q01, q99 = np.quantile(band_values, [0.01, 0.99])
    extra = (q99 - q01) * 0.4
    axes[current_ax_index].set(ylim=(q01 - extra, q99 + extra))
    
    axes[current_ax_index].set_ylabel(variable_name, fontsize=default_plot_kwargs['font_size'])
    axes[current_ax_index].set_title(title, fontweight="bold", size=16, pad=2)
    axes[current_ax_index].set_xlabel("")
    
"""                   
            mid_content = f"""
in_path = '{params['input_file']}'
# read example csv for HLS time series
if in_path.endswith('.csv'):
    data = pd.read_csv(in_path)
elif in_path.endswith('.xlsx') or in_path.endswith('.xls'):
    data = pd.read_excel(in_path)
else:
    raise ValueError("Unsupported file format")
# split the array by the column
date_column = '{params['date_column']}'  
data.columns = ['dates' if col == date_column else col for col in data.columns]
dates = data['dates'].values
dates = check_and_convert_dates(dates)

if not all(np.issubdtype(data[col].dtype, np.integer) for col in data.select_dtypes(include=[np.number]).columns):
    messagebox.showerror("Error", f"The data contains non-integer type numeric columns")

merge = np.stack([data[b].values for b in {params['selected_bands']}], axis=1)

qa_column = '{params['qa_column']}'  
if qa_column in data.columns:
    data.columns = ['qa' if col == qa_column else col for col in data.columns]
    qa = data['qa'].values
else:
    
    qa = np.zeros_like(dates, dtype=int)
    data['qa'] = qa
fitting_coefficients = True if '{params['fitting_curve']}' == 'Lasso' else False
"""
            
            if params['method'] == 'COLD':
                script_content = f"""
cold_result = cold_detect_flex(dates, merge, qa, float({params['Lam']}), p_cg=float({params['P_CG']}), conse=int({params['CONSE']}))        

sns.set_theme(style="darkgrid")
sns.set_context("notebook")

fig, ax = plt.subplots(figsize=(12, 5))

display_cold_result(data=np.column_stack((dates, merge, qa)), 
                band_names={params['selected_bands']}, 
                band_index={params['selected_bands']}.index('{params['display_band']}'), 
                indicator_band_index={params['selected_bands']}.index('{params['break_indicator']}'), 
                cold_result=cold_result, 
                axe=ax, 
                title="COLD")
plt.show()
"""

            elif params['method'] == 'S-CCD':
                if params['output'] == 'anomaly':
                    if params['fitting_curve'] == 'States':
                        script_content = f"""
sccd_result, anomaly = sccd_detect_flex(dates, merge, qa, float({params['Lam']}), p_cg=float({params['P_CG']}), conse=int({params['CONSE']}),output_anomaly=True, fitting_coefs=fitting_coefficients, trimodal={params['trimodal']})
sccd_result, states = sccd_detect_flex(dates, merge, qa, float({params['Lam']}), p_cg=float({params['P_CG']}), conse=int({params['CONSE']}), state_intervaldays=1, fitting_coefs=fitting_coefficients, trimodal={params['trimodal']})
                        
sns.set_theme(style="darkgrid")
sns.set_context("notebook")
fig, axes = plt.subplots(figsize=(12, 5))
plt.subplots_adjust(hspace=0.4)
                        

display_sccd_result_sif(data=np.column_stack((dates, merge, qa)),  
                    band_names={params['selected_bands']}, 
                    band_index={params['selected_bands']}.index('{params['display_band']}'), 
                    indicator_band_index={params['selected_bands']}.index('{params['break_indicator']}'), 
                    sccd_result=sccd_result,  
                    axe=axes, 
                    title="S-CCD anomaly",
                    states=states,
                    anomaly=anomaly,
                    trimodal={params['trimodal']})
                        
plt.show()    
"""
                    else:
                        script_content = f"""
sccd_result, anomaly = sccd_detect_flex(dates, merge, qa, float({params['Lam']}), p_cg=float({params['P_CG']}), conse=int({params['CONSE']}),output_anomaly=True, fitting_coefs=fitting_coefficients, trimodal={params['trimodal']})
sns.set_theme(style="darkgrid")
sns.set_context("notebook")
fig, axes = plt.subplots(figsize=(12, 5))
plt.subplots_adjust(hspace=0.4)


display_sccd_result_sif(data=np.column_stack((dates, merge, qa)),  
                    band_names={params['selected_bands']}, 
                    band_index={params['selected_bands']}.index('{params['display_band']}'), 
                    indicator_band_index={params['selected_bands']}.index('{params['break_indicator']}'), 
                    sccd_result=sccd_result, 
                    anomaly=anomaly, 
                    axe=axes, 
                    title="S-CCD anomaly",
                    trimodal={params['trimodal']})
                        
plt.show()     
"""
                
                elif params['output'] == 'state_components':
                    script_content = f"""
sccd_result, states = sccd_detect_flex(dates, merge, qa, float({params['Lam']}), p_cg=float({params['P_CG']}), conse=int({params['CONSE']}),output_anomaly=False, state_intervaldays=1, fitting_coefs=fitting_coefficients, trimodal={params['trimodal']})
                
sns.set_theme(style="darkgrid")
sns.set_context("notebook")
                    
n_subplots = 5 if {params['trimodal']} else 4
fig, axes = plt.subplots(n_subplots, 1, figsize=[11, 9], sharex=True)
plt.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.1)
                    
display_sccd_states_flex(data_df=data, 
                    axes=axes, 
                    states=states, 
                    band_name='{params['display_band']}',
                    band_index={params['selected_bands']}.index('{params['display_band']}'), 
                    variable_name='{params['display_band']}', 
                    title="S-CCD")
                    
plt.show()
"""
                
                elif params['output'] == 'breaks':
                    if params['fitting_curve'] == 'States': 
                        script_content = f"""
sccd_result, states = sccd_detect_flex(dates, merge, qa, float({params['Lam']}), p_cg=float({params['P_CG']}), conse=int({params['CONSE']}),output_anomaly=False, state_intervaldays=1, fitting_coefs=fitting_coefficients, trimodal={params['trimodal']})
                
sns.set_theme(style="darkgrid")
sns.set_context("notebook")

fig, ax = plt.subplots(figsize=(12, 5))
display_sccd_result_sif(data=np.column_stack((dates, merge, qa)), 
                    band_names={params['selected_bands']}, 
                    band_index={params['selected_bands']}.index('{params['display_band']}'), 
                    indicator_band_index={params['selected_bands']}.index('{params['break_indicator']}'), 
                    sccd_result=sccd_result, 
                    axe=ax, 
                    title="S-CCD",
                    states=states)
plt.show()
"""            
                    else:
                        script_content = f"""
sccd_result = sccd_detect_flex(dates, merge, qa, float({params['Lam']}), p_cg=float({params['P_CG']}), conse=int({params['CONSE']}),output_anomaly=False, fitting_coefs=fitting_coefficients, trimodal={params['trimodal']})

                
sns.set_theme(style="darkgrid")
sns.set_context("notebook")

fig, ax = plt.subplots(figsize=(12, 5))
display_sccd_result(data=np.column_stack((dates, merge, qa)), 
                band_names={params['selected_bands']}, 
                band_index={params['selected_bands']}.index('{params['display_band']}'), 
                indicator_band_index={params['selected_bands']}.index('{params['break_indicator']}'), 
                sccd_result=sccd_result, 
                axe=ax, 
                title="SCCD")
plt.show()
            """

        
            full_script = header_content + mid_content + script_content
            text_area.insert(tk.INSERT, full_script)
            
        except Exception as e:
            text_area.insert(tk.INSERT, f"Error getting source code: {str(e)}")
            
        text_area.config(state=tk.DISABLED)
        
        close_button = ttk.Button(
            script_window, 
            text="Close", 
            command=script_window.destroy
        )
        close_button.pack(pady=5)
    
    
    
    def run_analysis(self):
        """运行分析"""
        # 验证输入
        if self.df is None:
            messagebox.showerror("Error", "Please select a data file first")
            return
        
        if not self.selected_columns['date']:
            messagebox.showerror("Error", "Please select the date column")
            return
        
        if not self.selected_columns['display_band']:
            messagebox.showerror("Error", "Please select the display band column")
            return
        
        if not self.selected_columns['bands']:
            messagebox.showerror("Error", "Please select at least one band")
            return
        
        if not self.selected_columns['qa'] and self.qa_enable_var.get():
            messagebox.showerror("Error", "Please select the QA column")
            return
        
        
        try:
            p_cg = float(self.p_cg_var.get())
            if not (0.0 < p_cg < 1.0):  # P_CG 应该是 (0.0, 1.0] 范围内的浮点数
                messagebox.showerror("Error", "P_CG must be a float in the range (0.0, 1.0]")
                return
        except ValueError:
            messagebox.showerror("Error", "P_CG must be a valid float number")
            return

        # 验证 CONSE 参数
        try:
            conse = int(self.conse_var.get())
            if not (0 < conse <= 8):  # CONSE 应该是 (0, 8] 范围内的整数
                messagebox.showerror("Error", "CONSE must be an integer in the range (0, 8]")
                return
        except ValueError:
            messagebox.showerror("Error", "CONSE must be a valid integer")
            return
        
        # 获取output选项
        output_option = self.output_var.get()
        
        # 收集参数
        params = {
            'input_file': self.input_var.get(),
            'method': self.method_var.get(),
            'date_column': self.selected_columns['date'],
            'qa_column': self.selected_columns['qa'],
            'selected_bands': self.selected_columns['bands'],
            'break_indicator': self.selected_columns['break_indicator'],
            'display_band': self.selected_columns['display_band'],
            'P_CG': self.p_cg_var.get(),
            'CONSE': self.conse_var.get(),
            'output': output_option,  # 使用新的output参数
            'Lam': self.lam_var.get(),
            'trimodal': self.trimodal_var.get(),
            'fitting_curve': self.fitting_curve_var.get(),
        }
        # 保存参数以便在show_script中使用
        self.last_params = params
        # messagebox.showinfo("开始分析", f"开始执行变化检测分析\n方法: {params['method']}")
        print("分析参数:", params)
        def execute_change_detection(params):
            import numpy as np
            import os
            import pandas as pd
            from pyxccd import cold_detect_flex,sccd_detect_flex
            from pyxccd.common import cold_rec_cg
            from pyxccd.utils import read_data, getcategory_cold
            from datetime import date
            from typing import List, Tuple, Dict, Union, Optional
            import seaborn as sns
            import matplotlib.pyplot as plt
            from matplotlib.axes import Axes
            from pyxccd.common import SccdOutput, anomaly
            from pyxccd.utils import getcategory_sccd, defaults, getcategory_cold, predict_ref
            from matplotlib.lines import Line2D   
            from tkinter import messagebox

            def check_and_convert_dates(dates):
                """
                检查并转换日期列表/数组：
                1. 支持格式：数字（如733062）或字符串（如"8/1/1979"）
                2. 如果是字符串格式，转换为数字格式（序数日期）
                3. 严格验证日期范围（700000-800000）
                4. 返回转换后的整数格式日期数组（numpy.ndarray）
                """
                try:
                    # 转换为numpy数组统一处理
                    dates = np.array(dates) if not isinstance(dates, np.ndarray) else dates
                    
                    # 检查数组是否为空
                    if len(dates) == 0:
                        messagebox.showerror("Error", "Date data is empty")
                        return None
                    
                    # 检查每个元素的类型和范围
                    for i, date in enumerate(dates):
                        # 处理数字类型日期
                        if isinstance(date, (int, float, np.integer, np.floating)):
                            if not (700000 <= date <= 800000):  # 保留你的范围检查
                                messagebox.showerror("Error", f"Date value is not within the valid range (700000-800000): {date}")
                                return None
                        
                        # 处理字符串类型日期
                        elif isinstance(date, str):
                            try:
                                # 尝试解析日期字符串
                                pd.to_datetime(date, format='%m/%d/%Y')
                            except ValueError:
                                try:
                                    # 尝试其他可能的日期格式
                                    pd.to_datetime(date)
                                except ValueError:
                                    messagebox.showerror("Error", f"Date format error: {date}")
                                    return None
                        else:
                            messagebox.showerror("Error", f"Unsupported date format: {date}")
                            return None
                    
                    # 如果所有日期都是字符串格式，进行转换
                    if isinstance(dates[0], str):
                        try:
                            # 将字符串日期转换为datetime，然后转换为序数日期
                            dates = pd.to_datetime(dates, format='%m/%d/%Y')
                            dates = dates.to_series().apply(lambda x: x.toordinal()).values
                            
                            # 额外检查转换后的日期范围
                            if not np.all((700000 <= dates) & (dates <= 800000)):
                                invalid_dates = dates[(dates < 700000) | (dates > 800000)]
                                messagebox.showerror("Error", 
                                    f"The converted date is out of range (700000-800000): {invalid_dates[:5]}...")
                                return None
                        except Exception as e:
                            messagebox.showerror("Error", f"Date conversion failed: {str(e)}")
                            return None
                    
                    # 确保返回的是整数类型的numpy数组
                    return np.array(dates, dtype=np.int64) if not isinstance(dates, np.ndarray) else dates.astype(np.int64)
                
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred while processing the date: {str(e)}")
                    return None
            
            
            in_path = params['input_file']
            # read example csv for HLS time series
            if in_path.endswith('.csv'):
                data = pd.read_csv(in_path)
            elif in_path.endswith('.xlsx') or in_path.endswith('.xls'):
                data = pd.read_excel(in_path)
            else:
                raise ValueError("Unsupported file format")
            
            # split the array by the column
            data = data.rename(columns={params['date_column']: 'dates'})
            dates = data['dates'].values
            dates = check_and_convert_dates(dates)
            
            if not all(np.issubdtype(data[col].dtype, np.integer) for col in data.select_dtypes(include=[np.number]).columns):
                messagebox.showerror("Error", f"The data contains non-integer type numeric columns")
                
            merge = np.stack([data[b].values for b in params['selected_bands']], axis=1)
            if params['qa_column'] is not None:
                
                data = data.rename(columns={params['qa_column']: 'qa'})
                qa = data['qa'].values
            else:
                # 创建一个与 dates 长度相同的全零数组
                qa = np.zeros_like(dates, dtype=int)
                data['qa'] = qa
            

            
            
            def display_sccd_result_sif(
                data: np.ndarray,
                band_names: List[str],
                band_index: int,
                indicator_band_index: int,
                sccd_result: SccdOutput,
                axe: Axes,
                title: str = 'S-CCD',
                states: Optional[pd.DataFrame] = None,
                anomaly: Optional[anomaly] = None,
                trimodal: Optional[bool] = False,  
                plot_kwargs: Optional[Dict] = None
            ) -> Tuple[plt.Figure, List[plt.Axes]]:
                """
                Compare COLD and SCCD change detection algorithms by plotting their results side by side.
                
                This function takes time series remote sensing data, applies both COLD and SCCD algorithms,
                and visualizes the curve fitting and break detection results for comparison. 
                
                Parameters:
                -----------
                data : np.ndarray
                    Input data array with shape (n_observations, n_bands + 2) where:
                    - First column: ordinal dates (days since January 1, AD 1)
                    - Next n_bands columns: spectral band values
                    - Last column: QA flags (0-clear, 1-water, 2-shadow, 3-snow, 4-cloud)
                    
                band_names : List[str]
                    List of band names corresponding to the spectral bands in the data (e.g., ['red', 'nir'])
                    
                band_index : int
                    1-based index of the band to plot (e.g., 0 for first band, 1 for second band)
                    
                indicator_band_index : int
                    The band index used to determine break point colors (based on magnitude)
                    
                sccd_result: SccdOutput
                    Output of sccd_detect
                
                axe: Axes
                    An Axes object represents a single plot within that Figure
                
                title: Str
                    The figure title. The default is "S-CCD"
                    
                states: pd.DataFrame, optional
                    DataFrame containing model states for each time point (if provided, will use for fitting)
                    
                anomaly: anomaly, optional
                    The anomaly detection outputs
                    
                trimodal: bool, optional
                    If True, use 8 coefficients (including trimodal terms); if False, use 6 coefficients
                    
                plot_kwargs : Dict, optional
                    Additional keyword arguments to pass to the display function. Possible keys:
                    - 'marker_size': size of observation markers (default: 5)
                    - 'marker_alpha': transparency of markers (default: 0.7)
                    - 'line_color': color of model fit lines (default: 'orange')
                    - 'font_size': base font size (default: 14)
                    
                Returns:
                --------
                Tuple[plt.Figure, List[plt.Axes]]
                    A tuple containing the matplotlib Figure object and a list of Axes objects
                """
                w = np.pi * 2 / 365.25

                # Set default plot parameters
                default_plot_kwargs: Dict[str, Union[int, float, str]] = {
                    'marker_size': 5,
                    'marker_alpha': 0.7,
                    'line_color': 'orange',
                    'font_size': 14
                }
                if plot_kwargs is not None:
                    default_plot_kwargs.update(plot_kwargs)

                # Extract values with proper type casting
                font_size = default_plot_kwargs.get('font_size', 14)
                try:
                    title_font_size = int(font_size) + 2
                except (TypeError, ValueError):
                    title_font_size = 16 

                # Clean and prepare data
                data = data[np.all(np.isfinite(data), axis=1)]
                data_df = pd.DataFrame(data, columns=['dates'] + band_names + ['qa'])

                # Plot COLD results
                w = np.pi * 2 / 365.25
                slope_scale = 10000

                # Prepare clean data for COLD plot
                data_clean = data_df[(data_df['qa'] == 0) | (data_df['qa'] == 1)].copy()
                data_clean = data_clean[(data_clean >= 0).all(axis=1) & (data_clean.drop(columns="dates") <= 10000).all(axis=1)]
                calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in data_clean["dates"]]
                data_clean.loc[:, 'dates_formal'] = calendar_dates
                
                # Calculate y-axis limits
                band_name = band_names[band_index]
                band_values = data_clean[data_clean['qa'] == 0 | (data_clean['qa'] == 1)][band_name]
                q01, q99 = np.quantile(band_values, [0.01, 0.99])
                extra = (q99 - q01) * 0.4
                ylim_low = q01 - extra
                ylim_high = q99 + extra

                # Plot SCCD observations
                axe.plot(
                    'dates_formal', band_name, 'go',
                    markersize=default_plot_kwargs['marker_size'],
                    alpha=default_plot_kwargs['marker_alpha'],
                    data=data_clean
                )

                # Plot SCCD segments - NEW: use states if provided
                if states is not None:
                    # Build column names based on band_index
                    col_prefix = f"b{band_index}"
                    trend_col = f"{col_prefix}_trend"
                    annual_col = f"{col_prefix}_annual"
                    semiannual_col = f"{col_prefix}_semiannual"
                    trimodal_col = f"{col_prefix}_trimodal"
                    
                    # Check required columns exist
                    required_cols = [trend_col, annual_col, semiannual_col]
                    missing_cols = [col for col in required_cols if col not in states.columns]
                    if missing_cols:
                        raise ValueError(f"Missing required columns in states: {missing_cols}")
                    
                    # Convert dates
                    states["dates_formal"] = [pd.Timestamp.fromordinal(int(row)) for row in states["dates"]]
                    
                    # Calculate combined prediction (General)
                    has_trimodal = trimodal_col in states.columns
                    if has_trimodal:
                        states["General"] = states[trend_col] + states[annual_col] + states[semiannual_col] + states[trimodal_col]
                    else:
                        states["General"] = states[trend_col] + states[annual_col] + states[semiannual_col]
                    
                    # Plot fitted curve
                    g = sns.lineplot(
                        x="dates_formal", y="General",
                        data=states,
                        label="Model fit",
                        ax=axe,
                        color=default_plot_kwargs['line_color']
                    )
                    if g.legend_ is not None: 
                        g.legend_.remove()
                else:
                    # Original segment-by-segment plotting
                    for segment in sccd_result.rec_cg:
                        j = np.arange(segment['t_start'], segment['t_break'] + 1, 1)
                        # 使用 trimodal 布尔值判断系数数量
                        if trimodal:  # 8 coefficients
                            plot_df = pd.DataFrame(
                                {
                                'dates': j,
                                'trend': j * segment['coefs'][band_index][1] / slope_scale + segment['coefs'][band_index][0],
                                'annual': np.cos(w * j) * segment['coefs'][band_index][2] + np.sin(w * j) * segment['coefs'][band_index][3],
                                'semiannual': np.cos(2 * w * j) * segment['coefs'][band_index][4] + np.sin(2 * w * j) * segment['coefs'][band_index][5],
                                'trimodal': np.cos(3 * w * j) * segment['coefs'][band_index][6] + np.sin(3 * w * j) * segment['coefs'][band_index][7]
                            })
                        else:  # 6 coefficients
                            plot_df = pd.DataFrame(
                                {
                                'dates': j,
                                'trend': j * segment['coefs'][band_index][1] / slope_scale + segment['coefs'][band_index][0],
                                'annual': np.cos(w * j) * segment['coefs'][band_index][2] + np.sin(w * j) * segment['coefs'][band_index][3],
                                'semiannual': np.cos(2 * w * j) * segment['coefs'][band_index][4] + np.sin(2 * w * j) * segment['coefs'][band_index][5],
                                'trimodal': j * 0
                            })
                            
                        plot_df['predicted'] = (
                            plot_df['trend'] + 
                            plot_df['annual'] + 
                            plot_df['semiannual'] +
                            plot_df['trimodal']
                        )

                        # Convert dates and plot model fit
                        calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in plot_df["dates"]]
                        plot_df.loc[:, 'dates_formal'] = calendar_dates
                        g = sns.lineplot(
                            x="dates_formal", y="predicted",
                            data=plot_df,
                            label="Model fit",
                            ax=axe,
                            color=default_plot_kwargs['line_color']
                        )
                        if g.legend_ is not None: 
                            g.legend_.remove()

                    # Plot near-real-time projection for SCCD if available
                    if hasattr(sccd_result, 'nrt_mode') and (sccd_result.nrt_mode %10 == 1 or sccd_result.nrt_mode == 3 or sccd_result.nrt_mode %10 == 5):
                        recent_obs = sccd_result.nrt_model['obs_date_since1982'][sccd_result.nrt_model['obs_date_since1982']>0]
                        j = np.arange(
                            sccd_result.nrt_model['t_start_since1982'].item() + defaults['COMMON']['JULIAN_LANDSAT4_LAUNCH'], 
                            recent_obs[-1].item()+ defaults['COMMON']['JULIAN_LANDSAT4_LAUNCH']+1, 
                            1
                        )

                        # 使用 trimodal 布尔值判断系数数量
                        if trimodal:  # 8 coefficients
                            plot_df = pd.DataFrame(
                                {
                                'dates': j,
                                'trend': j * sccd_result.nrt_model['nrt_coefs'][band_index][1] / slope_scale + sccd_result.nrt_model['nrt_coefs'][band_index][0],
                                'annual': np.cos(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][2] + np.sin(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][3],
                                'semiannual': np.cos(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][4] + np.sin(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][5],
                                'trimodal': np.cos(3 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][6] + np.sin(3 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][7]
                            })
                        else:  # 6 coefficients
                            plot_df = pd.DataFrame(
                                {
                                'dates': j,
                                'trend': j * sccd_result.nrt_model['nrt_coefs'][band_index][1] / slope_scale + sccd_result.nrt_model['nrt_coefs'][band_index][0],
                                'annual': np.cos(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][2] + np.sin(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][3],
                                'semiannual': np.cos(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][4] + np.sin(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][5],
                                'trimodal': j * 0
                            })
                            
                        plot_df['predicted'] = plot_df['trend'] + plot_df['annual'] + plot_df['semiannual'] + plot_df['trimodal']
                        calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in plot_df["dates"]]
                        plot_df.loc[:, 'dates_formal'] = calendar_dates
                        g = sns.lineplot(
                            x="dates_formal", y="predicted",
                            data=plot_df,
                            label="Model fit",
                            ax=axe,
                            color=default_plot_kwargs['line_color']
                        )
                        if g.legend_ is not None: 
                            g.legend_.remove()
                                    
                # add manual legends
                if anomaly is not None:
                    legend_elements = [Line2D([0], [0], label=f'{band_names[indicator_band_index]} decrease break', color='k'),
                                        Line2D([0], [0], label=f'{band_names[indicator_band_index]} increase break', color='r'),
                                        Line2D([0], [0], marker='o', color="#EAEAF2",
                                        markerfacecolor="#EAEAF2", markeredgecolor="black",
                                        label=f'{band_names[indicator_band_index]} decrease anomalies', lw=0, markersize=8),
                                        Line2D([0], [0], marker='o', color="#EAEAF2",
                                        markerfacecolor="#EAEAF2", markeredgecolor="red",
                                        label=f'{band_names[indicator_band_index]} increase anomalies', lw=0, markersize=8)]
                else:
                    legend_elements = [Line2D([0], [0], label=f'{band_names[indicator_band_index]} decrease break', color='k'),
                                    Line2D([0], [0], label=f'{band_names[indicator_band_index]} increase break', color='r')]
                axe.legend(handles=legend_elements, loc='upper left', prop={'size': 9})
                
                # plot breaks
                for i in range(len(sccd_result.rec_cg)):
                    if sccd_result.rec_cg[i]['magnitude'][indicator_band_index] < 0:    
                        axe.axvline(pd.Timestamp.fromordinal(sccd_result.rec_cg[i]['t_break']), color='k')
                    else:
                        axe.axvline(pd.Timestamp.fromordinal(sccd_result.rec_cg[i]['t_break']), color='r')
                
                # plot anomalies if available
                if anomaly is not None:
                    # 使用 trimodal 布尔值判断系数数量
                    n_coefs = 8 if trimodal else 6
                    
                    for i in range(len(anomaly.rec_cg_anomaly)):
                        pred_ref = np.asarray(
                                [
                                    predict_ref(
                                        anomaly.rec_cg_anomaly[i]["coefs"][0],
                                        anomaly.rec_cg_anomaly[i]["obs_date_since1982"][i_conse].item()
                                        + defaults['COMMON']['JULIAN_LANDSAT4_LAUNCH'], num_coefficients=n_coefs
                                    ) for i_conse in range(3)
                                ]
                        )

                        cm = anomaly.rec_cg_anomaly[i]["obs"][0, 0: 3] - pred_ref
                        
                        if np.median(cm) > 0:
                            yc = data[data[:,0] == anomaly.rec_cg_anomaly[i]['t_break']][0][1]
                            axe.plot(pd.Timestamp.fromordinal(anomaly.rec_cg_anomaly[i]['t_break']), yc,'ro',fillstyle='none',markersize=8)         
                        else:
                            yc = data[data[:,0] == anomaly.rec_cg_anomaly[i]['t_break']][0][1]
                            axe.plot(pd.Timestamp.fromordinal(anomaly.rec_cg_anomaly[i]['t_break']), yc,'ko',fillstyle='none',markersize=8) 
                
                axe.set_ylabel(f"{band_name} * 10000", fontsize=default_plot_kwargs['font_size'])

                # Handle tick params with type safety
                tick_font_size = default_plot_kwargs['font_size']
                if isinstance(tick_font_size, (int, float)):
                    axe.tick_params(axis='x', labelsize=int(tick_font_size)-1)
                else:
                    axe.tick_params(axis='x', labelsize=13)  # fallback

                axe.set(ylim=(ylim_low, ylim_high))
                axe.set_xlabel("", fontsize=6)

                # Format spines
                for spine in axe.spines.values():
                    spine.set_edgecolor('black')
                title_font_size = int(font_size) + 2 if isinstance(font_size, (int, float)) else 16
                axe.set_title(title, fontweight="bold", size=title_font_size, pad=2)
                
            
            def display_cold_result(
                data: np.ndarray,
                band_names: List[str],
                band_index: int,
                indicator_band_index: int,
                cold_result: cold_rec_cg,
                axe: Axes,
                title: str = 'COLD',
                plot_kwargs: Optional[Dict] = None
            ) -> Tuple[plt.Figure, List[plt.Axes]]:
                """
                Compare COLD and SCCD change detection algorithms by plotting their results side by side.
                
                This function takes time series remote sensing data, applies both COLD algorithms,
                and visualizes the curve fitting and break detection results. 
                
                Parameters:
                -----------
                data : np.ndarray
                    Input data array with shape (n_observations, n_bands + 2) where:
                    - First column: ordinal dates (days since January 1, AD 1)
                    - Next n_bands columns: spectral band values
                    - Last column: QA flags (0-clear, 1-water, 2-shadow, 3-snow, 4-cloud)
                    
                band_names : List[str]
                    List of band names corresponding to the spectral bands in the data (e.g., ['red', 'nir'])
                    
                band_index : int
                    1-based index of the band to plot (e.g., 0 for first band, 1 for second band)
                
                axe: Axes
                    An Axes object represents a single plot within that Figure
                
                title: Str
                    The figure title. The default is "COLD"
                    
                plot_kwargs : Dict, optional
                    Additional keyword arguments to pass to the display function. Possible keys:
                    - 'marker_size': size of observation markers (default: 5)
                    - 'marker_alpha': transparency of markers (default: 0.7)
                    - 'line_color': color of model fit lines (default: 'orange')
                    - 'font_size': base font size (default: 14)
                    
                Returns:
                --------
                Tuple[plt.Figure, List[plt.Axes]]
                    A tuple containing the matplotlib Figure object and a list of Axes objects
                    (top axis is COLD results, bottom axis is SCCD results)
                
                """
                w = np.pi * 2 / 365.25

                # Set default plot parameters
                default_plot_kwargs: Dict[str, Union[int, float, str]] = {
                    'marker_size': 5,
                    'marker_alpha': 0.7,
                    'line_color': 'orange',
                    'font_size': 14
                }
                if plot_kwargs is not None:
                    default_plot_kwargs.update(plot_kwargs)

                # Extract values with proper type casting
                font_size = default_plot_kwargs.get('font_size', 14)
                try:
                    title_font_size = int(font_size) + 2
                except (TypeError, ValueError):
                    title_font_size = 16 


                # Clean and prepare data
                data = data[np.all(np.isfinite(data), axis=1)]
                data_df = pd.DataFrame(data, columns=['dates'] + band_names + ['qa'])

                # Plot COLD results
                w = np.pi * 2 / 365.25
                slope_scale = 10000

                # Prepare clean data for COLD plot
                data_clean = data_df[(data_df['qa'] == 0) | (data_df['qa'] == 1)].copy()
                data_clean =  data_clean[(data_clean >= 0).all(axis=1) & (data_clean.drop(columns="dates") <= 10000).all(axis=1)]
                calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in data_clean["dates"]]
                data_clean.loc[:, 'dates_formal'] = calendar_dates
                
                # Calculate y-axis limits
                band_name = band_names[band_index]
                band_values = data_clean[data_clean['qa'] == 0][band_name]
                q01, q99 = np.quantile(band_values, [0.01, 0.99])
                extra = (q99 - q01) * 0.4
                ylim_low = q01 - extra
                ylim_high = q99 + extra

                # Plot COLD observations
                axe.plot(
                    'dates_formal', band_name, 'go',
                    markersize=default_plot_kwargs['marker_size'],
                    alpha=default_plot_kwargs['marker_alpha'],
                    data=data_clean
                )

                # Plot COLD segments
                for segment in cold_result:
                    j = np.arange(segment['t_start'], segment['t_end'] + 1, 1)
                    plot_df = pd.DataFrame({
                        'dates': j,
                        'trend': j * segment['coefs'][band_index][1] / slope_scale + segment['coefs'][band_index][0],
                        'annual': np.cos(w * j) * segment['coefs'][band_index][2] + np.sin(w * j) * segment['coefs'][band_index][3],
                        'semiannual': np.cos(2 * w * j) * segment['coefs'][band_index][4] + np.sin(2 * w * j) * segment['coefs'][band_index][5],
                        'trimodel': np.cos(3 * w * j) * segment['coefs'][band_index][6] + np.sin(3 * w * j) * segment['coefs'][band_index ][7]
                    })
                    plot_df['predicted'] = (
                        plot_df['trend'] + 
                        plot_df['annual'] + 
                        plot_df['semiannual'] + 
                        plot_df['trimodel']
                    )

                    # Convert dates and plot model fit
                    calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in plot_df["dates"]]
                    plot_df.loc[:, 'dates_formal'] = calendar_dates
                    g = sns.lineplot(
                        x="dates_formal", y="predicted",
                        data=plot_df,
                        label="Model fit",
                        ax=axe,
                        color=default_plot_kwargs['line_color']
                    )
                    if g.legend_ is not None: 
                        g.legend_.remove()

                # add manual legends
                legend_elements = [Line2D([0], [0], label=f'{band_names[indicator_band_index]} decrease break', color='k'),
                                Line2D([0], [0], label=f'{band_names[indicator_band_index]} increase break', color='r')]
                axe.legend(handles=legend_elements, loc='upper left', prop={'size': 9})
                
                # plot breaks
                for i in range(len(cold_result)):
                    if  cold_result[i]['change_prob'] == 100:
                        if cold_result[i]['magnitude'][indicator_band_index] < 0:
                            axe.axvline(pd.Timestamp.fromordinal(cold_result[i]['t_break']), color='k')
                        else:
                            axe.axvline(pd.Timestamp.fromordinal(cold_result[i]['t_break']), color='r')
                
                axe.set_ylabel(f"{band_name} * 10000", fontsize=default_plot_kwargs['font_size'])

                # Handle tick params with type safety
                tick_font_size = default_plot_kwargs['font_size']
                if isinstance(tick_font_size, (int, float)):
                    axe.tick_params(axis='x', labelsize=int(tick_font_size)-1)
                else:
                    axe.tick_params(axis='x', labelsize=13)  # fallback

                axe.set(ylim=(ylim_low, ylim_high))
                axe.set_xlabel("", fontsize=6)

                # Format spines
                for spine in axe.spines.values():
                    spine.set_edgecolor('black')
                title_font_size = int(font_size) + 2 if isinstance(font_size, (int, float)) else 16
                axe.set_title(title, fontweight="bold", size=title_font_size, pad=2)
            
            def display_sccd_result(
                data: np.ndarray,
                band_names: List[str],
                band_index: int,
                indicator_band_index: int,
                sccd_result: SccdOutput,
                axe: Axes,
                title: str = 'S-CCD',
                states: Optional[pd.DataFrame] = None,
                plot_kwargs: Optional[Dict] = None
            ) -> Tuple[plt.Figure, List[plt.Axes]]:
                """
                Compare COLD and SCCD change detection algorithms by plotting their results side by side.
                
                This function takes time series remote sensing data, applies both COLD and SCCD algorithms,
                and visualizes the curve fitting and break detection results for comparison. 
                
                Parameters:
                -----------
                data : np.ndarray
                    Input data array with shape (n_observations, n_bands + 2) where:
                    - First column: ordinal dates (days since January 1, AD 1)
                    - Next n_bands columns: spectral band values
                    - Last column: QA flags (0-clear, 1-water, 2-shadow, 3-snow, 4-cloud)
                    
                band_names : List[str]
                    List of band names corresponding to the spectral bands in the data (e.g., ['red', 'nir'])
                    
                band_index : int
                    1-based index of the band to plot (e.g., 0 for first band, 1 for second band)
                    
                indicator_band_index : int
                    The band index used to determine break point colors (based on magnitude)
                    
                sccd_result: SccdOutput
                    Output of sccd_detect
                
                axe: Axes
                    An Axes object represents a single plot within that Figure
                
                title: Str
                    The figure title. The default is "S-CCD"
                    
                states: pd.DataFrame, optional
                    DataFrame containing model states for each time point (if provided, will use for fitting)
                    
                plot_kwargs : Dict, optional
                    Additional keyword arguments to pass to the display function. Possible keys:
                    - 'marker_size': size of observation markers (default: 5)
                    - 'marker_alpha': transparency of markers (default: 0.7)
                    - 'line_color': color of model fit lines (default: 'orange')
                    - 'font_size': base font size (default: 14)
                    
                Returns:
                --------
                Tuple[plt.Figure, List[plt.Axes]]
                    A tuple containing the matplotlib Figure object and a list of Axes objects
                    (top axis is COLD results, bottom axis is SCCD results)
                """
                w = np.pi * 2 / 365.25

                # Set default plot parameters
                default_plot_kwargs: Dict[str, Union[int, float, str]] = {
                    'marker_size': 5,
                    'marker_alpha': 0.7,
                    'line_color': 'orange',
                    'font_size': 14
                }
                if plot_kwargs is not None:
                    default_plot_kwargs.update(plot_kwargs)

                # Extract values with proper type casting
                font_size = default_plot_kwargs.get('font_size', 14)
                try:
                    title_font_size = int(font_size) + 2
                except (TypeError, ValueError):
                    title_font_size = 16 

                # Clean and prepare data
                data = data[np.all(np.isfinite(data), axis=1)]
                data_df = pd.DataFrame(data, columns=['dates'] + band_names + ['qa'])

                # Plot COLD results
                w = np.pi * 2 / 365.25
                slope_scale = 10000

                # Prepare clean data for COLD plot
                data_clean = data_df[(data_df['qa'] == 0) | (data_df['qa'] == 1)].copy()
                data_clean = data_clean[(data_clean >= 0).all(axis=1) & (data_clean.drop(columns="dates") <= 10000).all(axis=1)]
                calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in data_clean["dates"]]
                data_clean.loc[:, 'dates_formal'] = calendar_dates
                
                # Calculate y-axis limits
                band_name = band_names[band_index]
                band_values = data_clean[data_clean['qa'] == 0 | (data_clean['qa'] == 1)][band_name]
                q01, q99 = np.quantile(band_values, [0.01, 0.99])
                extra = (q99 - q01) * 0.4
                ylim_low = q01 - extra
                ylim_high = q99 + extra

                # Plot SCCD observations
                axe.plot(
                    'dates_formal', band_name, 'go',
                    markersize=default_plot_kwargs['marker_size'],
                    alpha=default_plot_kwargs['marker_alpha'],
                    data=data_clean
                )

                # Plot SCCD segments - NEW: use states if provided
                if states is not None:
                    # Build column names based on band_index
                    col_prefix = f"b{band_index}"
                    trend_col = f"{col_prefix}_trend"
                    annual_col = f"{col_prefix}_annual"
                    semiannual_col = f"{col_prefix}_semiannual"
                    trimodal_col = f"{col_prefix}_trimodal"
                    
                    # Check required columns exist
                    required_cols = [trend_col, annual_col, semiannual_col]
                    missing_cols = [col for col in required_cols if col not in states.columns]
                    if missing_cols:
                        raise ValueError(f"Missing required columns in states: {missing_cols}")
                    
                    # Convert dates
                    states["dates_formal"] = [pd.Timestamp.fromordinal(int(row)) for row in states["dates"]]
                    
                    # Calculate combined prediction (General)
                    has_trimodal = trimodal_col in states.columns
                    if has_trimodal:
                        states["General"] = states[trend_col] + states[annual_col] + states[semiannual_col] + states[trimodal_col]
                    else:
                        states["General"] = states[trend_col] + states[annual_col] + states[semiannual_col]
                    
                    # Plot fitted curve
                    g = sns.lineplot(
                        x="dates_formal", y="General",
                        data=states,
                        label="Model fit",
                        ax=axe,
                        color=default_plot_kwargs['line_color']
                    )
                    if g.legend_ is not None: 
                        g.legend_.remove()
                else:
                    # Original segment-by-segment plotting
                    for segment in sccd_result.rec_cg:
                        j = np.arange(segment['t_start'], segment['t_break'] + 1, 1)
                        if len(segment['coefs'][band_index]) == 8:
                            plot_df = pd.DataFrame(
                                {
                                'dates': j,
                                'trend': j * segment['coefs'][band_index][1] / slope_scale + segment['coefs'][band_index][0],
                                'annual': np.cos(w * j) * segment['coefs'][band_index][2] + np.sin(w * j) * segment['coefs'][band_index][3],
                                'semiannual': np.cos(2 * w * j) * segment['coefs'][band_index][4] + np.sin(2 * w * j) * segment['coefs'][band_index][5],
                                'trimodal': np.cos(3 * w * j) * segment['coefs'][band_index][6] + np.sin(3 * w * j) * segment['coefs'][band_index][7]
                            })
                        else:
                            plot_df = pd.DataFrame(
                                {
                                'dates': j,
                                'trend': j * segment['coefs'][band_index][1] / slope_scale + segment['coefs'][band_index][0],
                                'annual': np.cos(w * j) * segment['coefs'][band_index][2] + np.sin(w * j) * segment['coefs'][band_index][3],
                                'semiannual': np.cos(2 * w * j) * segment['coefs'][band_index][4] + np.sin(2 * w * j) * segment['coefs'][band_index][5],
                                'trimodal': j * 0
                            })
                        plot_df['predicted'] = (
                            plot_df['trend'] + 
                            plot_df['annual'] + 
                            plot_df['semiannual'] +
                            plot_df['trimodal']
                        )

                        # Convert dates and plot model fit
                        calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in plot_df["dates"]]
                        plot_df.loc[:, 'dates_formal'] = calendar_dates
                        g = sns.lineplot(
                            x="dates_formal", y="predicted",
                            data=plot_df,
                            label="Model fit",
                            ax=axe,
                            color=default_plot_kwargs['line_color']
                        )
                        if g.legend_ is not None: 
                            g.legend_.remove()

                # Plot near-real-time projection for SCCD if available
                if hasattr(sccd_result, 'nrt_mode') and (sccd_result.nrt_mode %10 == 1 or sccd_result.nrt_mode == 3 or sccd_result.nrt_mode %10 == 5):
                    recent_obs = sccd_result.nrt_model['obs_date_since1982'][sccd_result.nrt_model['obs_date_since1982']>0]
                    j = np.arange(
                        sccd_result.nrt_model['t_start_since1982'].item() + defaults['COMMON']['JULIAN_LANDSAT4_LAUNCH'], 
                        recent_obs[-1].item()+ defaults['COMMON']['JULIAN_LANDSAT4_LAUNCH']+1, 
                        1
                    )

                    if len(sccd_result.nrt_model['nrt_coefs'][band_index]) == 8:
                        plot_df = pd.DataFrame(
                            {
                            'dates': j,
                            'trend': j * sccd_result.nrt_model['nrt_coefs'][band_index][1] / slope_scale + sccd_result.nrt_model['nrt_coefs'][band_index][0],
                            'annual': np.cos(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][2] + np.sin(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][3],
                            'semiannual': np.cos(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][4] + np.sin(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][5],
                            'trimodal': np.cos(3 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][6] + np.sin(3 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][7]
                        })
                    else:
                        plot_df = pd.DataFrame(
                            {
                            'dates': j,
                            'trend': j * sccd_result.nrt_model['nrt_coefs'][band_index][1] / slope_scale + sccd_result.nrt_model['nrt_coefs'][band_index][0],
                            'annual': np.cos(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][2] + np.sin(w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][3],
                            'semiannual': np.cos(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][4] + np.sin(2 * w * j) * sccd_result.nrt_model['nrt_coefs'][band_index][5],
                            'trimodal': j * 0
                        })
                        
                    plot_df['predicted'] = plot_df['trend'] + plot_df['annual'] + plot_df['semiannual'] + plot_df['trimodal']
                    calendar_dates = [pd.Timestamp.fromordinal(int(row)) for row in plot_df["dates"]]
                    plot_df.loc[:, 'dates_formal'] = calendar_dates
                    g = sns.lineplot(
                        x="dates_formal", y="predicted",
                        data=plot_df,
                        label="Model fit",
                        ax=axe,
                        color=default_plot_kwargs['line_color']
                    )
                    if g.legend_ is not None: 
                        g.legend_.remove()

                # add manual legends
                legend_elements = [Line2D([0], [0], label=f'{band_names[indicator_band_index]} decrease break', color='k'),
                                Line2D([0], [0], label=f'{band_names[indicator_band_index]} increase break', color='r')]
                axe.legend(handles=legend_elements, loc='upper left', prop={'size': 9})
                
                # plot breaks
                for i in range(len(sccd_result.rec_cg)):
                    if sccd_result.rec_cg[i]['magnitude'][indicator_band_index] < 0:
                        axe.axvline(pd.Timestamp.fromordinal(sccd_result.rec_cg[i]['t_break']), color='k')
                    else:
                        axe.axvline(pd.Timestamp.fromordinal(sccd_result.rec_cg[i]['t_break']), color='r')
                
                axe.set_ylabel(f"{band_name} * 10000", fontsize=default_plot_kwargs['font_size'])

                # Handle tick params with type safety
                tick_font_size = default_plot_kwargs['font_size']
                if isinstance(tick_font_size, (int, float)):
                    axe.tick_params(axis='x', labelsize=int(tick_font_size)-1)
                else:
                    axe.tick_params(axis='x', labelsize=13)  # fallback

                axe.set(ylim=(ylim_low, ylim_high))
                axe.set_xlabel("", fontsize=6)

                # Format spines
                for spine in axe.spines.values():
                    spine.set_edgecolor('black')
                title_font_size = int(font_size) + 2 if isinstance(font_size, (int, float)) else 16
                axe.set_title(title, fontweight="bold", size=title_font_size, pad=2)
            
            def display_sccd_states_flex(
                data_df: pd.DataFrame,
                states: pd.DataFrame,
                axes: Axes,
                variable_name: str,
                title: str,
                band_name: str,
                band_index: int,  
                plot_kwargs: Optional[Dict] = None
            ):
                """显示S-CCD状态结果的灵活函数"""
                default_plot_kwargs = {
                    'marker_size': 5,
                    'marker_alpha': 0.7,
                    'line_color': 'orange',
                    'font_size': 14
                }
                if plot_kwargs is not None:
                    default_plot_kwargs.update(plot_kwargs)

                # 构建列名前缀
                col_prefix = f"b{band_index}"  # 使用b0, b1等格式
                
                # 构建完整的列名
                trend_col = f"{col_prefix}_trend"
                annual_col = f"{col_prefix}_annual"
                semiannual_col = f"{col_prefix}_semiannual"
                trimodal_col = f"{col_prefix}_trimodal"  # 可能不存在
                
                # 验证列是否存在（trimodal可选）
                required_cols = [trend_col, annual_col, semiannual_col]
                missing_cols = [col for col in required_cols if col not in states.columns]
                if missing_cols:
                    raise ValueError(f"缺少必要的列: {missing_cols}。可用列: {states.columns.tolist()}")

                has_trimodal = trimodal_col in states.columns  # 检查是否有trimodal列

                # 转换日期格式
                states["dates_formal"] = [pd.Timestamp.fromordinal(int(row)) for row in states["dates"]]

                # 绘制趋势分量（第1个子图）
                extra = (np.max(states[trend_col]) - np.min(states[trend_col])) / 4
                axes[0].set(ylim=(np.min(states[trend_col]) - extra, np.max(states[trend_col]) + extra))
                sns.lineplot(x="dates_formal", y=trend_col, data=states, ax=axes[0], color="orange")
                axes[0].set(ylabel="Trend")

                # 绘制年周期分量（第2个子图）
                extra = (np.max(states[annual_col]) - np.min(states[annual_col])) / 4
                axes[1].set(ylim=(np.min(states[annual_col]) - extra, np.max(states[annual_col]) + extra))
                sns.lineplot(x="dates_formal", y=annual_col, data=states, ax=axes[1], color="orange")
                axes[1].set(ylabel="Annual cycle")

                # 绘制半年周期分量（第3个子图）
                extra = (np.max(states[semiannual_col]) - np.min(states[semiannual_col])) / 4
                axes[2].set(ylim=(np.min(states[semiannual_col]) - extra, np.max(states[semiannual_col]) + extra))
                sns.lineplot(x="dates_formal", y=semiannual_col, data=states, ax=axes[2], color="orange")
                axes[2].set(ylabel="Semi-annual cycle")

                current_ax_index = 3  # 当前子图索引

                # 如果有trimodal列，绘制trimodal分量（第4个子图）
                if has_trimodal:
                    extra = (np.max(states[trimodal_col]) - np.min(states[trimodal_col])) / 4
                    axes[3].set(ylim=(np.min(states[trimodal_col]) - extra, np.max(states[trimodal_col]) + extra))
                    sns.lineplot(x="dates_formal", y=trimodal_col, data=states, ax=axes[3], color="orange")
                    axes[3].set(ylabel="Trimodal cycle")
                    current_ax_index += 1  # 如果绘制了trimodal，则下一个子图索引+1

                # 绘制原始数据（第current_ax_index个子图）
                data_clean = data_df[(data_df["qa"] == 0) | (data_df['qa'] == 1)].copy()
                data_clean["dates"] = check_and_convert_dates(data_clean["dates"])
                data_clean["dates_formal"] = [pd.Timestamp.fromordinal(int(row)) for row in data_clean["dates"]]
                axes[current_ax_index].plot(
                    'dates_formal', variable_name, 'go',
                    markersize=default_plot_kwargs['marker_size'],
                    alpha=default_plot_kwargs['marker_alpha'],
                    data=data_clean
                )

                # 绘制拟合结果（第current_ax_index个子图）
                if has_trimodal:
                    states["General"] = states[annual_col] + states[trend_col] + states[semiannual_col] + states[trimodal_col]
                else:
                    states["General"] = states[annual_col] + states[trend_col] + states[semiannual_col]
                
                sns.lineplot(x="dates_formal", y="General", data=states, label="fit", ax=axes[current_ax_index], color="orange")
                
                # 设置y轴范围
                band_values = data_df[data_df['qa'] == 0][variable_name]
                q01, q99 = np.quantile(band_values, [0.01, 0.99])
                extra = (q99 - q01) * 0.4
                axes[current_ax_index].set(ylim=(q01 - extra, q99 + extra))
                
                axes[current_ax_index].set_ylabel(variable_name, fontsize=default_plot_kwargs['font_size'])
                axes[current_ax_index].set_title(title, fontweight="bold", size=16, pad=2)
                axes[current_ax_index].set_xlabel("")

            params['fitting_coefficients'] = True if params['fitting_curve'] == 'Lasso' else False
            #选择COLD
            if params['method'] == 'COLD':
                cold_result = cold_detect_flex(dates, merge, qa,float(params['Lam']), p_cg=float(params['P_CG']), conse=int(params['CONSE']))        
                sns.set_theme(style="darkgrid")
                sns.set_context("notebook")

                fig, ax = plt.subplots(figsize=(12, 5))

                display_cold_result(data=np.column_stack((dates, merge, qa)), band_names=params['selected_bands'], band_index=params['selected_bands'].index(params['display_band']), indicator_band_index=params['selected_bands'].index(params['break_indicator']), cold_result=cold_result, axe=ax, title="COLD")
                print("6. 绘图完成，准备显示")
                plt.show(block=True)
                print("plt.show()已调用")
            #选择S-CCD    
            elif params['method'] == 'S-CCD':
                if params['output'] == 'anomaly':
                    if params['fitting_curve'] == 'States':
                        sccd_result, anomaly = sccd_detect_flex(dates, merge, qa, float(params['Lam']), p_cg=float(params['P_CG']), conse=int(params['CONSE']),output_anomaly=True, fitting_coefs=params['fitting_coefficients'], trimodal=params['trimodal'])
                        sccd_result, states = sccd_detect_flex(dates, merge, qa, float(params['Lam']), p_cg=float(params['P_CG']), conse=int(params['CONSE']), state_intervaldays=1, fitting_coefs=params['fitting_coefficients'], trimodal=params['trimodal'])
                        
                        sns.set_theme(style="darkgrid")
                        sns.set_context("notebook")
                        fig, axes = plt.subplots(figsize=(12, 5))
                        plt.subplots_adjust(hspace=0.4)
                        
                        display_sccd_result_sif(data=np.column_stack((dates, merge, qa)),  band_names=params['selected_bands'], band_index=params['selected_bands'].index(params['display_band']), indicator_band_index=params['selected_bands'].index(params['break_indicator']), sccd_result=sccd_result,  axe=axes, title="S-CCD anomaly",states=states,anomaly=anomaly,trimodal=params['trimodal'])
                        
                        plt.show()    
                        
                    else:
                        sccd_result, anomaly = sccd_detect_flex(dates, merge, qa, float(params['Lam']), p_cg=float(params['P_CG']), conse=int(params['CONSE']),output_anomaly=True, fitting_coefs=params['fitting_coefficients'], trimodal=params['trimodal'])
                        sns.set_theme(style="darkgrid")
                        sns.set_context("notebook")
                        fig, axes = plt.subplots(figsize=(12, 5))
                        plt.subplots_adjust(hspace=0.4)

                        display_sccd_result_sif(data=np.column_stack((dates, merge, qa)),  band_names=params['selected_bands'], band_index=params['selected_bands'].index(params['display_band']), indicator_band_index=params['selected_bands'].index(params['break_indicator']), sccd_result=sccd_result, anomaly=anomaly, trimodal=params['trimodal'], axe=axes, title="S-CCD anomaly")
                        
                        plt.show()     
            
                elif params['output'] == 'state_components':
                    sccd_result, states = sccd_detect_flex(dates, merge, qa, float(params['Lam']), p_cg=float(params['P_CG']), conse=int(params['CONSE']),output_anomaly=False, state_intervaldays=1, fitting_coefs=params['fitting_coefficients'], trimodal=params['trimodal'])
                
                    sns.set_theme(style="darkgrid")
                    sns.set_context("notebook")
                    
                    n_subplots = 5 if params['trimodal'] else 4
                    fig, axes = plt.subplots(n_subplots, 1, figsize=[11, 9], sharex=True)
                    plt.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.1)
                    
                    display_sccd_states_flex(data_df=data, axes=axes, states=states, band_name=params['display_band'],band_index=params['selected_bands'].index(params['display_band']), variable_name=params['display_band'], title="S-CCD")
                    
                    plt.show()
                
                else:    
                
                    sccd_result, states = sccd_detect_flex(dates, merge, qa, float(params['Lam']), p_cg=float(params['P_CG']), conse=int(params['CONSE']),output_anomaly=False, state_intervaldays=1, fitting_coefs=params['fitting_coefficients'], trimodal=params['trimodal'])
                
                    sns.set_theme(style="darkgrid")
                    sns.set_context("notebook")

                    fig, ax = plt.subplots(figsize=(12, 5))
                    if params['fitting_curve'] == 'States':
                        display_sccd_result_sif(data=np.column_stack((dates, merge, qa)), band_names=params['selected_bands'], band_index=params['selected_bands'].index(params['display_band']), indicator_band_index=params['selected_bands'].index(params['break_indicator']), sccd_result=sccd_result, axe=ax, title="S-CCD",states=states)
                        plt.show()
                    else:
                        display_sccd_result(data=np.column_stack((dates, merge, qa)), band_names=params['selected_bands'], band_index=params['selected_bands'].index(params['display_band']), indicator_band_index=params['selected_bands'].index(params['break_indicator']), sccd_result=sccd_result, axe=ax, title="SCCD")
                        plt.show()
        execute_change_detection(params)
            
def main():
    root = tk.Tk()
    app = ChangeDetectionApp(root)
    root.mainloop()

if __name__ == "__main__":

    main()
