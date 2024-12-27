# main.py
import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from config import USERS
from utils.data_handler import DataHandler

# 初始化數據處理器
data_handler = DataHandler()

# 頁面配置
st.set_page_config(
    page_title="專案進度追蹤系統",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'tasks' not in st.session_state:
    st.session_state.tasks = data_handler.load_tasks()

# 登入功能
def login():
    if not st.session_state.logged_in:
        st.title("專案進度追蹤系統")
        
        # 創建登入表單
        with st.form("login_form"):
            username = st.text_input("用戶名")
            password = st.text_input("密碼", type="password")
            submit = st.form_submit_button("登入")
            
            if submit:
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = USERS[username]["role"]
                    st.rerun()
                else:
                    st.error("用戶名或密碼錯誤")
        
        # 添加訪客登入選項
        if st.button("以訪客身份瀏覽"):
            st.session_state.logged_in = True
            st.session_state.username = "guest"
            st.session_state.role = "viewer"
            st.rerun()
        
        return False
    return True

def add_new_task(task_name, start_date, end_date, category, status, notes, checklist_text):
    if task_name and start_date and end_date:
        if end_date >= start_date:
            checklist = []
            if checklist_text:
                checklist = [
                    {"item": item.strip(), "completed": False}
                    for item in checklist_text.split('\n')
                    if item.strip()
                ]
            
            new_task = {
                'id': len(st.session_state.tasks),
                'Task': task_name,
                'Start': start_date,
                'Finish': end_date,
                'Category': category,
                'Status': status,
                'Notes': notes,
                'Checklist': checklist,
                'Created_by': st.session_state.username,
                'Created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            # 使用 data_handler 添加新任務
            st.session_state.tasks = data_handler.add_task(st.session_state.tasks, new_task)
            st.success("任務添加成功！")
            st.rerun()
        else:
            st.error("結束日期必須晚於或等於開始日期！")
    else:
        st.warning("請填寫所有必要信息！")

def show_task_table():
    st.header("任務列表")
    
    for task in st.session_state.tasks:
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        with col1:
            if st.button(f"📋 {task['Task']}", key=f"task_{task['id']}", help="點擊查看任務詳情"):
                st.session_state.current_task = task
                st.switch_page("pages/task_detail.py")
        with col2:
            st.write(f"開始: {task['Start']}")
        with col3:
            st.write(f"結束: {task['Finish']}")
        with col4:
            st.write(f"狀態: {task['Status']}")
        with col5:
            if task['Checklist']:
                completed = sum(1 for item in task['Checklist'] if item['completed'])
                total = len(task['Checklist'])
                progress = (completed / total) * 100
                st.write(f"進度: {progress:.1f}%")
            else:
                st.write("進度: 0%")

def show_charts():
    # 創建兩列布局用於顯示圓餅圖
    col1, col2 = st.columns(2)

    # 第一列：狀態分佈圓餅圖
    with col1:
        st.subheader("任務狀態分佈")
        df_status = pd.DataFrame(st.session_state.tasks)
        if not df_status.empty:
            status_counts = df_status['Status'].value_counts()
            fig_status = go.Figure(data=[go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.3,
                marker=dict(colors=['rgb(220, 0, 0)', 'rgb(255, 165, 0)', 'rgb(0, 255, 0)']),
            )])
            fig_status.update_layout(
                showlegend=True,
                height=400,
                annotations=[dict(text='狀態', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("暫無數據")

    # 第二列：類別分佈圓餅圖
    with col2:
        st.subheader("任務類別分佈")
        df_category = pd.DataFrame(st.session_state.tasks)
        if not df_category.empty:
            category_counts = df_category['Category'].value_counts()
            fig_category = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                hole=0.3,
            )
            fig_category.update_layout(
                showlegend=True,
                height=400,
                annotations=[dict(text='類別', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.info("暫無數據")
    
    # 創建甘特圖
    st.header("甘特圖")
    
    # 設置顏色映射
    colors = {
        '未開始': 'rgb(220, 0, 0)',     # 紅色
        '進行中': 'rgb(255, 165, 0)',   # 橙色
        '已完成': 'rgb(0, 255, 0)'      # 綠色
    }

    # 創建甘特圖數據
    df_gantt = pd.DataFrame(st.session_state.tasks)[['Task', 'Start', 'Finish', 'Status']]
    
    if not df_gantt.empty:
        # 使用 plotly.figure_factory 創建甘特圖
        fig = ff.create_gantt(
            df_gantt,
            colors=colors,
            index_col='Status',
            show_colorbar=True,
            group_tasks=True,
            showgrid_x=True,
            showgrid_y=True,
        )
        
        # 更新圖表布局
        fig.update_layout(
            title='項目進度甘特圖',
            xaxis_title='日期',
            yaxis_title='任務',
            height=400 + (len(df_gantt) * 30),
            font=dict(size=10),
            showlegend=True,
            # 調整邊距
            margin=dict(l=50, r=50, t=50, b=50),
            # 添加懸停模式設置
            hovermode='closest'
        )
        
        # 更新懸停信息格式
        for trace in fig.data:
            trace.update(
                hovertemplate="<b>%{text}</b><br>" +
                            "開始: %{base|%Y-%m-%d}<br>" +
                            "結束: %{x|%Y-%m-%d}<br>" +
                            "狀態: " + trace.name +
                            "<extra></extra>"
            )
        
        # 顯示圖表
        st.plotly_chart(fig, use_container_width=True, key="gantt_chart")
        
        # 添加圖表說明
        with st.expander("甘特圖使用說明"):
            st.markdown("""
            - 點擊任務名稱可查看詳細信息
            - 懸停在任務條上可查看時間信息
            - 可以通過圖例篩選不同狀態的任務
            - 使用右上角工具欄可以縮放、平移或下載圖表
            """)
    else:
        st.info("暫無任務數據，請添加任務後查看甘特圖")

def main():
    # 側邊欄
    with st.sidebar:
        st.write(f"當前用戶: {st.session_state.username}")
        if st.button("登出"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.rerun()
        
        # 只有管理員可以看到添加任務的選項
        if st.session_state.role == "admin":
            st.header("添加新任務")
            
            task_name = st.text_input("任務名稱", key="new_task_name")
            checklist_text = st.text_area("檢查項目清單", key="new_checklist")
            start_date = st.date_input("開始日期", key="new_start")
            end_date = st.date_input("結束日期", key="new_end")
            category = st.text_input("任務類別", key="new_category")
            status = st.selectbox("任務狀態", ["未開始", "進行中", "已完成"], key="new_status")
            notes = st.text_area("注意事項", key="new_notes")
            
            if st.button("添加任務", key="add_task_button"):
                add_new_task(task_name, start_date, end_date, category, status, notes, checklist_text)

    # 主要內容區域
    st.title("專案進度追蹤")
    
    # 添加項目概況
    if st.session_state.tasks:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_tasks = len(st.session_state.tasks)
            st.metric("總任務數", total_tasks)
        
        with col2:
            completed_tasks = len([t for t in st.session_state.tasks if t['Status'] == '已完成'])
            st.metric("已完成任務", completed_tasks)
        
        with col3:
            in_progress = len([t for t in st.session_state.tasks if t['Status'] == '進行中'])
            st.metric("進行中任務", in_progress)
        
        with col4:
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            st.metric("完成率", f"{completion_rate:.1f}%")
        
        # 顯示任務表格
        show_task_table()
        
        # 顯示圖表
        show_charts()
    else:
        st.info("目前沒有任務數據")

    # CSV匯入功能
    st.header("導入現有數據")
    uploaded_file = st.file_uploader("上傳CSV文件", type=['csv'], key="file_uploader")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df['Start'] = pd.to_datetime(df['Start']).dt.date
            df['Finish'] = pd.to_datetime(df['Finish']).dt.date
            
            tasks = []
            for i, row in df.iterrows():
                task = {
                    'id': i,
                    'Task': row['Task'],
                    'Start': row['Start'],
                    'Finish': row['Finish'],
                    'Category': row['Category'],
                    'Status': row['Status'],
                    'Notes': row.get('Notes', ''),
                    'Checklist': [],
                    'Progress': 0,
                    'Created_by': st.session_state.username,
                    'Created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                tasks.append(task)
            
            st.session_state.tasks = tasks
            data_handler.save_tasks(tasks)  # 保存導入的數據
            st.success("數據導入成功！")
            st.rerun()
        except Exception as e:
            st.error(f"導入失敗：{str(e)}")

# 運行應用
if login():
    main()