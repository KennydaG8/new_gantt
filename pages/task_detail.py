# pages/task_detail.py
import streamlit as st
from datetime import datetime

# 設置頁面配置
st.set_page_config(page_title="任務詳情", layout="wide")

# 檢查登入狀態
if not st.session_state.get('logged_in', False):
    st.error("請先登入系統")
    st.stop()

# 獲取當前任務
current_task = st.session_state.get('current_task')

if current_task:
    st.title(f"任務詳情: {current_task['Task']}")
    
    # 顯示創建信息
    st.caption(f"創建者: {current_task.get('Created_by', '未知')} | 創建時間: {current_task.get('Created_at', '未知')}")
    
    # 創建三列布局
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.subheader("基本信息")
        st.write(f"**開始日期:** {current_task['Start']}")
        st.write(f"**結束日期:** {current_task['Finish']}")
        st.write(f"**任務類別:** {current_task['Category']}")
        
        # 只有管理員可以更改狀態
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
                # 只有管理員可以更改檢查項目狀態
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
    
    # 只有管理員可以添加新的檢查項目
    if st.session_state.role == "admin":
        st.subheader("添加新檢查項目")
        col1, col2 = st.columns([3, 1])
        with col1:
            new_item = st.text_input("新檢查項目", key="new_item")
        with col2:
            if st.button("添加項目", type="primary", key="add_item") and new_item:
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
    
    # 底部按鈕區
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("返回甘特圖", type="primary", key="return_button"):
            st.switch_page("main.py")
    
    # 只有管理員可以使用這些功能
    if st.session_state.role == "admin":
        with col2:
            if st.button("清空所有檢查項目", key="clear_button"):
                if st.session_state.current_task:
                    for task in st.session_state.tasks:
                        if task['id'] == current_task['id']:
                            task['Checklist'] = []
                            current_task['Checklist'] = []
                            st.success("已清空所有檢查項目")
                            st.rerun()
        
        with col3:
            if current_task['Status'] != '已完成':
                if st.button("標記為已完成", type="primary", key="complete_button"):
                    for task in st.session_state.tasks:
                        if task['id'] == current_task['id']:
                            task['Status'] = '已完成'
                            current_task['Status'] = '已完成'
                            # 同時將所有檢查項目標記為完成
                            for item in task.get('Checklist', []):
                                item['completed'] = True
                            st.success("任務已標記為完成！")
                            st.rerun()
            else:
                if st.button("重新打開任務", key="reopen_button"):
                    for task in st.session_state.tasks:
                        if task['id'] == current_task['id']:
                            task['Status'] = '進行中'
                            current_task['Status'] = '進行中'
                            st.success("任務已重新打開！")
                            st.rerun()

    # 添加任務歷史記錄顯示
    with st.expander("任務歷史記錄"):
        st.write("最近更新：")
        st.write(f"創建時間：{current_task.get('Created_at', '未知')}")
        st.write(f"創建者：{current_task.get('Created_by', '未知')}")
        
        # 如果有更多歷史記錄，可以在這裡顯示
        if 'history' in current_task:
            for record in current_task['history']:
                st.write(f"{record['time']} - {record['action']} by {record['user']}")

else:
    st.error("無法找到任務信息！")
    if st.button("返回甘特圖", key="error_return"):
        st.switch_page("main.py")