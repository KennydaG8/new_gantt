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

# 設置頁面配置
st.set_page_config(
    page_title="專案進度追蹤系統",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加自定義 CSS
st.markdown("""
    <style>
    /* 整體應用樣式 */
    .stApp {
        background-color: #1E1E1E;
    }
    
    /* 標題樣式 */
    h1 {
        background: linear-gradient(45deg, #2C3E50, #3498DB);
        color: white !important;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* 卡片樣式 */
    .metric-card {
        background: #2D2D2D;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        background: linear-gradient(45deg, #2C3E50, #3498DB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .metric-label {
        color: #CCCCCC;
        font-size: 16px;
        font-weight: 500;
    }
    
    /* 任務列表樣式 */
    .task-row {
        background: #2D2D2D;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    .task-row:hover {
        transform: scale(1.01);
    }
    .task-title {
        font-size: 18px;
        font-weight: 600;
        color: #3498DB;
        margin-bottom: 10px;
    }
    .task-info {
        color: #CCCCCC;
        font-size: 14px;
    }
    .task-status {
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }
    .status-pending {
        background-color: #2C3E50;
        color: #FFF;
    }
    .status-progress {
        background-color: #2980B9;
        color: #FFF;
    }
    .status-completed {
        background-color: #27AE60;
        color: #FFF;
    }
    
    /* 任務按鈕樣式 */
    .stButton > button {
        background: linear-gradient(45deg, #2C3E50, #3498DB);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 500;
        transition: all 0.3s ease;
        width: 100%;
        margin: 5px 0;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* 側邊欄樣式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #2C3E50, #3498DB);
    }
    .css-1d391kg .stButton > button {
        background: #2D2D2D;
        color: #3498DB;
    }
    
    /* 進度條容器 */
    .progress-container {
        margin-top: 10px;
        background: #2D2D2D;
        border-radius: 10px;
        height: 6px;
        overflow: hidden;
    }
    
    /* 進度條 */
    .progress-bar {
        height: 100%;
        background: linear-gradient(45deg, #2C3E50, #3498DB);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* 進度條樣式 */
    .stProgress > div > div {
        background-color: #3498DB;
    }

    /* 輸入框樣式 */
    .stTextInput > div > div > input {
        background-color: #2D2D2D;
        color: white;
        border-color: #3D3D3D;
    }
    
    /* 下拉選單樣式 */
    .stSelectbox > div > div {
        background-color: #2D2D2D;
        color: white;
    }
    
    /* 文本區域樣式 */
    .stTextArea textarea {
        background-color: #2D2D2D;
        color: white;
        border-color: #3D3D3D;
    }
    </style>
""", unsafe_allow_html=True)

# 初始化 session state


if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'tasks' not in st.session_state:
    st.session_state.tasks = data_handler.load_tasks()
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'main'
if 'current_task' not in st.session_state:
    st.session_state.current_task = None
    
def show_task_table():
    for task in st.session_state.tasks:
        status_class = get_status_class(task['Status'])
        progress = calculate_progress(task)
        
        # 使用HTML美化外觀，但保留Streamlit按鈕功能
        st.markdown(f"""
            <div class="task-row">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex-grow: 1;">
                        <div class="task-title">{task['Task']}</div>
                        <div class="task-info">
                            <span>開始: {task['Start']}</span> | 
                            <span>結束: {task['Finish']}</span> | 
                            <span class="task-status {status_class}">{task['Status']}</span>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 保留原有的功能性按鈕，但使用更漂亮的樣式
        col1, col2 = st.columns([2, 8])
        with col1:
            if st.button(f"📋 查看詳情", key=f"task_{task['id']}", help="點擊查看任務詳情"):
                st.session_state.current_task = task
                st.session_state.current_view = 'detail'
                st.rerun()
        
        # 顯示進度條
        with col2:
            if task['Checklist']:
                completed = sum(1 for item in task['Checklist'] if item['completed'])
                total = len(task['Checklist'])
                progress = (completed / total) * 100
                st.markdown(f"""
                    <div style="margin-top: 10px;">
                        <div style="background: #eee; border-radius: 10px; height: 6px;">
                            <div style="width: {progress}%; height: 100%; background: #2193b0; border-radius: 10px;"></div>
                        </div>
                        <div style="text-align: right; font-size: 12px; color: #666; margin-top: 5px;">
                            進度: {progress:.1f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="text-align: right; font-size: 12px; color: #666;">
                        進度: 0%
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
        
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
                annotations=[dict(text='狀態', x=0.5, y=0.5, font_size=20, showarrow=False)],
                paper_bgcolor='#2D2D2D',  # 添加這行
                plot_bgcolor='#2D2D2D',   # 添加這行
                font=dict(color='white')   # 添加這行
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
                annotations=[dict(text='類別', x=0.5, y=0.5, font_size=20, showarrow=False)],
                paper_bgcolor='#2D2D2D',  # 添加這行
                plot_bgcolor='#2D2D2D',   # 添加這行
                font=dict(color='white')   # 添加這行
            )
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.info("暫無數據")

    # 創建甘特圖
    st.header("甘特圖")
    colors = {
        '未開始': 'rgb(220, 0, 0)',
        '進行中': 'rgb(255, 165, 0)',
        '已完成': 'rgb(0, 255, 0)'
    }

    df_gantt = pd.DataFrame(st.session_state.tasks)[['Task', 'Start', 'Finish', 'Status']]
    if not df_gantt.empty:
        fig = ff.create_gantt(
            df_gantt,
            colors=colors,
            index_col='Status',
            show_colorbar=True,
            group_tasks=True,
            showgrid_x=True,
            showgrid_y=True,
        )
        fig.update_layout(
            title='項目進度甘特圖',
            xaxis_title='日期',
            yaxis_title='任務',
            height=400 + (len(df_gantt) * 30),
            font=dict(size=10, color='white'),  # 修改這行
            showlegend=True,
            paper_bgcolor='#2D2D2D',  # 添加這行
            plot_bgcolor='#2D2D2D',   # 添加這行
            xaxis=dict(  # 添加這部分
                gridcolor='#444444',
                tickcolor='white',
                tickfont=dict(color='white')
            ),
            yaxis=dict(  # 添加這部分
                gridcolor='#444444',
                tickcolor='white',
                tickfont=dict(color='white')
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暫無任務數據")
        
def get_status_class(status):
    if status == '未開始':
        return 'status-pending'
    elif status == '進行中':
        return 'status-progress'
    else:
        return 'status-completed'


def show_main_view():
    # 主要內容區域
    st.title("專案進度追蹤")
    
    if st.session_state.tasks:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(st.session_state.tasks)}</div>
                    <div class="metric-label">總任務數</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            completed_tasks = len([t for t in st.session_state.tasks if t['Status'] == '已完成'])
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{completed_tasks}</div>
                    <div class="metric-label">已完成任務</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            in_progress = len([t for t in st.session_state.tasks if t['Status'] == '進行中'])
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{in_progress}</div>
                    <div class="metric-label">進行中任務</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            completion_rate = (completed_tasks / len(st.session_state.tasks) * 100) if st.session_state.tasks else 0
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{completion_rate:.1f}%</div>
                    <div class="metric-label">完成率</div>
                </div>
            """, unsafe_allow_html=True)
        
        show_task_table()
        show_charts()

def show_metrics():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(st.session_state.tasks)}</div>
                <div class="metric-label">總任務數</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        completed_tasks = len([t for t in st.session_state.tasks if t['Status'] == '已完成'])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{completed_tasks}</div>
                <div class="metric-label">已完成任務</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        in_progress = len([t for t in st.session_state.tasks if t['Status'] == '進行中'])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{in_progress}</div>
                <div class="metric-label">進行中任務</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        completion_rate = (completed_tasks / len(st.session_state.tasks) * 100) if st.session_state.tasks else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{completion_rate:.1f}%</div>
                <div class="metric-label">完成率</div>
            </div>
        """, unsafe_allow_html=True)


def show_detail_view():
    current_task = st.session_state.current_task
    
    # 返回按鈕
    if st.button("⬅️ 返回主頁", type="primary"):
        st.session_state.current_view = 'main'
        st.session_state.current_task = None
        st.rerun()

    st.title(f"任務詳情: {current_task['Task']}")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.subheader("基本信息")
        st.write(f"**開始日期:** {current_task['Start']}")
        st.write(f"**結束日期:** {current_task['Finish']}")
        st.write(f"**任務類別:** {current_task['Category']}")
        
        if st.session_state.role == "admin":
            new_status = st.selectbox(
                "當前狀態",
                ["未開始", "進行中", "已完成"],
                index=["未開始", "進行中", "已完成"].index(current_task['Status']),
                key="status_select"
            )
            if new_status != current_task['Status']:
                for task in st.session_state.tasks:
                    if task['id'] == current_task['id']:
                        task['Status'] = new_status
                        current_task['Status'] = new_status
                        st.success("狀態更新成功！")
                        st.rerun()
        else:
            st.write(f"**當前狀態:** {current_task['Status']}")
    
    with col2:
        st.subheader("注意事項")
        if st.session_state.role == "admin":
            notes = st.text_area(
                "編輯注意事項",
                value=current_task.get('Notes', ''),
                height=200,
                key="notes_area"
            )
            if notes != current_task.get('Notes', ''):
                for task in st.session_state.tasks:
                    if task['id'] == current_task['id']:
                        task['Notes'] = notes
                        current_task['Notes'] = notes
        else:
            st.write(current_task.get('Notes', '無注意事項'))
    
    with col3:
        st.subheader("任務進度")
        if current_task.get('Checklist'):
            completed = sum(1 for item in current_task['Checklist'] if item['completed'])
            total = len(current_task['Checklist'])
            progress = (completed / total) * 100
            st.progress(progress / 100)
            st.write(f"完成進度: {progress:.1f}%")
            
            st.write(f"總項目數: {total}")
            st.write(f"已完成項目: {completed}")
            st.write(f"待完成項目: {total - completed}")
        else:
            st.write("尚未添加檢查項目")
    
    # 檢查清單
    st.header("檢查項目列表")
    if 'Checklist' in current_task and current_task['Checklist']:
        for i, item in enumerate(current_task['Checklist']):
            col1, col2, col3 = st.columns([0.1, 1, 0.1])
            with col1:
                if st.session_state.role == "admin":
                    checked = st.checkbox(
                        label=f"項目 {i+1}",
                        value=item['completed'],
                        key=f"check_{i}",
                        label_visibility="collapsed"
                    )
                    if checked != item['completed']:
                        for task in st.session_state.tasks:
                            if task['id'] == current_task['id']:
                                task['Checklist'][i]['completed'] = checked
                                current_task['Checklist'][i]['completed'] = checked
                                st.rerun()
                else:
                    st.write("✓" if item['completed'] else "○")
            
            with col2:
                st.write(item['item'])
            
            with col3:
                if st.session_state.role == "admin" and st.button("刪除", key=f"delete_{i}"):
                    for task in st.session_state.tasks:
                        if task['id'] == current_task['id']:
                            task['Checklist'].pop(i)
                            current_task['Checklist'].pop(i)
                            st.rerun()
    
    # 添加新的檢查項目
    if st.session_state.role == "admin":
        st.subheader("添加新檢查項目")
        new_item = st.text_input("新檢查項目", key="new_item")
        if st.button("添加項目", type="primary") and new_item:
            for task in st.session_state.tasks:
                if task['id'] == current_task['id']:
                    if 'Checklist' not in task:
                        task['Checklist'] = []
                    task['Checklist'].append({
                        "item": new_item,
                        "completed": False
                    })
                    current_task['Checklist'] = task['Checklist']
                    st.success("新檢查項目添加成功！")
                    st.rerun()
                    
def calculate_progress(task):
    if task['Checklist']:
        completed = sum(1 for item in task['Checklist'] if item['completed'])
        return (completed / len(task['Checklist'])) * 100
    return 0


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
                        st.session_state.tasks.append(new_task)
                        st.success("任務添加成功！")
                        st.rerun()
                    else:
                        st.error("結束日期必須晚於或等於開始日期！")
                else:
                    st.warning("請填寫所有必要信息！")

    # 根據當前視圖顯示相應的內容
    if st.session_state.current_view == 'main':
        show_main_view()
    else:
        show_detail_view()

    # CSV匯入功能
    st.header("導入現有數據")
    uploaded_file = st.file_uploader("上傳CSV文件", type=['csv'])
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
            st.success("數據導入成功！")
            st.rerun()
        except Exception as e:
            st.error(f"導入失敗：{str(e)}")

# 運行應用
if login():
    main()
