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
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        with col1:
            if st.button(f"📋 {task['Task']}", key=f"task_{task['id']}", help="點擊查看任務詳情"):
                st.session_state.current_task = task
                st.session_state.current_view = 'detail'
                st.rerun()
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
            font=dict(size=10),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暫無任務數據")

def show_main_view():
    # 主要內容區域
    st.title("專案進度追蹤")
    
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
        
        show_task_table()
        show_charts()

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
