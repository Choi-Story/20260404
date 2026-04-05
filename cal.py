import sys
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QDialog, QLineEdit, QTextEdit, QMessageBox, QListWidget,
                             QListWidgetItem, QCalendarWidget)
from PySide6.QtCore import Qt, QDate, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush


class ScheduleManager:
    """일정 데이터 관리"""
    def __init__(self):
        self.data_file = Path.home() / ".calendar_schedules.json"
        self.schedules = self.load_schedules()
    
    def load_schedules(self):
        """JSON 파일에서 일정 로드"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_schedules(self):
        """일정을 JSON 파일에 저장"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.schedules, f, ensure_ascii=False, indent=2)
    
    def get_schedules(self, date_str):
        """특정 날짜의 일정 가져오기"""
        return self.schedules.get(date_str, [])
    
    def add_schedule(self, date_str, title, description):
        """일정 추가"""
        if date_str not in self.schedules:
            self.schedules[date_str] = []
        
        schedule = {
            'id': len(self.schedules.get(date_str, [])),
            'title': title,
            'description': description,
            'date': date_str
        }
        self.schedules[date_str].append(schedule)
        self.save_schedules()
        return schedule
    
    def update_schedule(self, date_str, schedule_id, title, description):
        """일정 수정"""
        if date_str in self.schedules:
            for schedule in self.schedules[date_str]:
                if schedule['id'] == schedule_id:
                    schedule['title'] = title
                    schedule['description'] = description
                    self.save_schedules()
                    return True
        return False
    
    def delete_schedule(self, date_str, schedule_id):
        """일정 삭제"""
        if date_str in self.schedules:
            self.schedules[date_str] = [
                s for s in self.schedules[date_str] if s['id'] != schedule_id
            ]
            if not self.schedules[date_str]:
                del self.schedules[date_str]
            self.save_schedules()
            return True
        return False


class ScheduleDialog(QDialog):
    """일정 추가/수정 다이얼로그"""
    def __init__(self, parent=None, date_str="", schedule=None):
        super().__init__(parent)
        self.date_str = date_str
        self.schedule = schedule
        self.init_ui()
        
        if schedule:
            self.title_input.setText(schedule['title'])
            self.description_input.setText(schedule['description'])
    
    def init_ui(self):
        self.setWindowTitle("일정 입력" if not self.schedule else "일정 수정")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # 날짜 표시
        date_label = QLabel(f"날짜: {self.date_str}")
        date_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(date_label)
        
        # 제목 입력
        layout.addWidget(QLabel("제목:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("일정 제목을 입력하세요")
        layout.addWidget(self.title_input)
        
        # 설명 입력
        layout.addWidget(QLabel("설명:"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("일정 설명을 입력하세요")
        layout.addWidget(self.description_input)
        
        # 저장 버튼
        button_layout = QHBoxLayout()
        save_btn = QPushButton("저장")
        cancel_btn = QPushButton("취소")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_schedule_data(self):
        return {
            'title': self.title_input.text(),
            'description': self.description_input.toPlainText()
        }


class ScheduleListDialog(QDialog):
    """날짜별 일정 목록 보기 및 관리"""
    schedule_updated = Signal()
    
    def __init__(self, parent=None, date_str="", schedules=None, manager=None):
        super().__init__(parent)
        self.date_str = date_str
        self.manager = manager
        self.init_ui()
        self.refresh_schedules(schedules or [])
    
    def init_ui(self):
        self.setWindowTitle(f"{self.date_str} 의 일정")
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout()
        
        # 날짜 표시
        date_label = QLabel(f"{self.date_str}")
        date_font = QFont("Arial", 14, QFont.Bold)
        date_label.setFont(date_font)
        layout.addWidget(date_label)
        
        # 일정 목록
        self.schedule_list = QListWidget()
        layout.addWidget(self.schedule_list)
        
        # 버튼들
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("새 일정 추가")
        edit_btn = QPushButton("수정")
        delete_btn = QPushButton("삭제")
        close_btn = QPushButton("닫기")
        
        add_btn.clicked.connect(self.add_schedule)
        edit_btn.clicked.connect(self.edit_schedule)
        delete_btn.clicked.connect(self.delete_schedule)
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def refresh_schedules(self, schedules):
        """일정 목록 새로고침"""
        self.schedule_list.clear()
        for schedule in schedules:
            item_text = f"{schedule['title']}"
            if schedule['description']:
                item_text += f"\n  {schedule['description'][:50]}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, schedule['id'])
            self.schedule_list.addItem(item)
    
    def add_schedule(self):
        """새로운 일정 추가"""
        dialog = ScheduleDialog(self, self.date_str)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_schedule_data()
            if data['title'].strip():
                self.manager.add_schedule(self.date_str, data['title'], data['description'])
                schedules = self.manager.get_schedules(self.date_str)
                self.refresh_schedules(schedules)
                self.schedule_updated.emit()
            else:
                QMessageBox.warning(self, "경고", "제목을 입력해주세요")
    
    def edit_schedule(self):
        """일정 수정"""
        current_item = self.schedule_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "경고", "수정할 일정을 선택해주세요")
            return
        
        schedule_id = current_item.data(Qt.UserRole)
        schedules = self.manager.get_schedules(self.date_str)
        schedule = next((s for s in schedules if s['id'] == schedule_id), None)
        
        if schedule:
            dialog = ScheduleDialog(self, self.date_str, schedule)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_schedule_data()
                if data['title'].strip():
                    self.manager.update_schedule(self.date_str, schedule_id, 
                                                data['title'], data['description'])
                    schedules = self.manager.get_schedules(self.date_str)
                    self.refresh_schedules(schedules)
                    self.schedule_updated.emit()
                else:
                    QMessageBox.warning(self, "경고", "제목을 입력해주세요")
    
    def delete_schedule(self):
        """일정 삭제"""
        current_item = self.schedule_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "경고", "삭제할 일정을 선택해주세요")
            return
        
        reply = QMessageBox.question(self, "확인", "정말 삭제하시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            schedule_id = current_item.data(Qt.UserRole)
            self.manager.delete_schedule(self.date_str, schedule_id)
            schedules = self.manager.get_schedules(self.date_str)
            self.refresh_schedules(schedules)
            self.schedule_updated.emit()


class CalendarApp(QMainWindow):
    """메인 달력 애플리케이션"""
    def __init__(self):
        super().__init__()
        self.manager = ScheduleManager()
        self.current_date = QDate.currentDate()
        self.init_ui()
        self.show()
    
    def init_ui(self):
        self.setWindowTitle("📅 나의 일정 (My Calendar)")
        self.setGeometry(100, 100, 900, 700)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 상단 제목
        title = QLabel("📅 나의 일정")
        title_font = QFont("Arial", 24, QFont.Bold)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # 캘린더와 일정 리스트를 담을 레이아웃
        content_layout = QHBoxLayout()
        
        # 왼쪽: 캘린더
        calendar_layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_clicked)
        self.update_calendar_colors()
        calendar_layout.addWidget(self.calendar)
        
        # 네비게이션 버튼
        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("◀ 이전 월")
        next_btn = QPushButton("다음 월 ▶")
        prev_btn.clicked.connect(self.prev_month)
        next_btn.clicked.connect(self.next_month)
        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(next_btn)
        calendar_layout.addLayout(nav_layout)
        
        content_layout.addLayout(calendar_layout, 1)
        
        # 오른쪽: 선택된 날짜의 일정
        right_layout = QVBoxLayout()
        
        selected_date_label = QLabel("선택된 날짜")
        selected_font = QFont("Arial", 12, QFont.Bold)
        selected_date_label.setFont(selected_font)
        right_layout.addWidget(selected_date_label)
        
        self.date_display = QLabel()
        date_display_font = QFont("Arial", 16, QFont.Bold)
        self.date_display.setFont(date_display_font)
        right_layout.addWidget(self.date_display)
        
        right_layout.addWidget(QLabel("일정 목록:"))
        
        self.today_schedule_list = QListWidget()
        right_layout.addWidget(self.today_schedule_list)
        
        # 일정 관리 버튼
        schedule_btn_layout = QHBoxLayout()
        add_schedule_btn = QPushButton("+ 새 일정 추가")
        view_schedule_btn = QPushButton("📋 일정 보기")
        
        add_schedule_btn.clicked.connect(self.add_schedule_quick)
        view_schedule_btn.clicked.connect(self.view_schedules)
        
        schedule_btn_layout.addWidget(add_schedule_btn)
        schedule_btn_layout.addWidget(view_schedule_btn)
        right_layout.addLayout(schedule_btn_layout)
        
        content_layout.addLayout(right_layout, 1)
        
        main_layout.addLayout(content_layout)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # 초기 날짜 설정
        self.on_date_changed(self.calendar.selectedDate())
    
    def update_calendar_colors(self):
        """일정이 있는 날짜를 표시"""
        for date_str in self.manager.schedules.keys():
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                qdate = QDate(date_obj.year, date_obj.month, date_obj.day)
                
                # 일정이 있는 날짜 표시
                self.calendar.setDateTextFormat(qdate, QFont("Arial", 10, QFont.Bold))
            except:
                pass
    
    def on_date_clicked(self, qdate):
        """날짜 클릭 시"""
        self.on_date_changed(qdate)
    
    def on_date_changed(self, qdate):
        """선택된 날짜 변경"""
        self.current_date = qdate
        date_str = qdate.toString("yyyy-MM-dd")
        
        # 날짜 표시
        date_korean = qdate.toString("yyyy년 M월 d일 (ddd)")
        day_names = ["월", "화", "수", "목", "금", "토", "일"]
        day_name = day_names[qdate.dayOfWeek() - 1] if qdate.dayOfWeek() <= 7 else ""
        self.date_display.setText(f"{qdate.toString('yyyy-MM-dd')} ({day_name}요일)")
        
        # 해당 날짜의 일정 표시
        schedules = self.manager.get_schedules(date_str)
        self.today_schedule_list.clear()
        
        if schedules:
            for schedule in schedules:
                item_text = f"✓ {schedule['title']}"
                if schedule['description']:
                    item_text += f"\n  {schedule['description'][:40]}..."
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, schedule['id'])
                self.today_schedule_list.addItem(item)
        else:
            item = QListWidgetItem("이 날짜에 일정이 없습니다.")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.today_schedule_list.addItem(item)
    
    def add_schedule_quick(self):
        """빠른 일정 추가"""
        date_str = self.current_date.toString("yyyy-MM-dd")
        dialog = ScheduleDialog(self, date_str)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_schedule_data()
            if data['title'].strip():
                self.manager.add_schedule(date_str, data['title'], data['description'])
                self.update_calendar_colors()
                self.on_date_changed(self.current_date)
            else:
                QMessageBox.warning(self, "경고", "제목을 입력해주세요")
    
    def view_schedules(self):
        """일정 상세 보기 및 관리"""
        date_str = self.current_date.toString("yyyy-MM-dd")
        schedules = self.manager.get_schedules(date_str)
        
        dialog = ScheduleListDialog(self, date_str, schedules, self.manager)
        dialog.schedule_updated.connect(self.on_schedule_updated)
        dialog.exec()
    
    def on_schedule_updated(self):
        """일정이 업데이트된 후"""
        self.update_calendar_colors()
        self.on_date_changed(self.current_date)
    
    def prev_month(self):
        """이전 달로 이동"""
        self.calendar.showPreviousMonth()
    
    def next_month(self):
        """다음 달로 이동"""
        self.calendar.showNextMonth()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 스타일시트 적용
    app.setStyle('Fusion')
    
    window = CalendarApp()
    sys.exit(app.exec())
