import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)

class MemberManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원정보 관리 프로그램 (PyQt5)")
        self.setGeometry(300, 200, 600, 400)
        self.members = []  # 회원 정보 리스트 (딕셔너리)
        self.selected_row = None  # 현재 선택된 행

        # 메인 위젯 & 레이아웃
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        form_layout = QHBoxLayout()

        # 입력 폼(이름, 이메일, 나이)
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.age_input = QLineEdit()
        form_layout.addWidget(QLabel("이름"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("이메일"))
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(QLabel("나이"))
        form_layout.addWidget(self.age_input)

        # 버튼(등록/수정/삭제)
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("등록")
        self.add_btn.clicked.connect(self.add_member)
        self.edit_btn = QPushButton("수정")
        self.edit_btn.clicked.connect(self.edit_member)
        self.del_btn = QPushButton("삭제")
        self.del_btn.clicked.connect(self.delete_member)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.del_btn)

        # 테이블(회원목록)
        self.table = QTableWidget(0, 3)  # row 0, col 3
        self.table.setHorizontalHeaderLabels(["이름", "이메일", "나이"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)

        # 레이아웃 정리
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.table)
        self.setCentralWidget(main_widget)

    def add_member(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        age = self.age_input.text().strip()

        if not (name and email and age):
            QMessageBox.warning(self, "경고", "모든 정보를 입력하세요.")
            return

        # 이메일 중복 체크
        for m in self.members:
            if m['이메일'] == email:
                QMessageBox.warning(self, "경고", "이미 등록된 이메일입니다.")
                return

        member = {"이름": name, "이메일": email, "나이": age}
        self.members.append(member)
        self.update_table()
        self.clear_form()

    def edit_member(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "경고", "수정할 회원을 선택하세요.")
            return

        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        age = self.age_input.text().strip()
        if not (name and email and age):
            QMessageBox.warning(self, "경고", "모든 정보를 입력하세요.")
            return

        # 이메일 변경 시 중복 체크
        for i, m in enumerate(self.members):
            if i != self.selected_row and m['이메일'] == email:
                QMessageBox.warning(self, "경고", "이미 등록된 이메일입니다.")
                return

        self.members[self.selected_row] = {"이름": name, "이메일": email, "나이": age}
        self.update_table()
        self.clear_form()

    def delete_member(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "경고", "삭제할 회원을 선택하세요.")
            return

        confirm = QMessageBox.question(self, "확인", "정말 삭제하시겠습니까?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            del self.members[self.selected_row]
            self.update_table()
            self.clear_form()

    def update_table(self):
        self.table.setRowCount(0)
        for member in self.members:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(member["이름"]))
            self.table.setItem(row, 1, QTableWidgetItem(member["이메일"]))
            self.table.setItem(row, 2, QTableWidgetItem(member["나이"]))
        self.selected_row = None

    def clear_form(self):
        self.name_input.clear()
        self.email_input.clear()
        self.age_input.clear()
        self.table.clearSelection()
        self.selected_row = None

    def on_cell_clicked(self, row, column):
        self.selected_row = row
        member = self.members[row]
        self.name_input.setText(member["이름"])
        self.email_input.setText(member["이메일"])
        self.age_input.setText(member["나이"])

    def on_cell_double_clicked(self, row, column):
        # 더블클릭 시 바로 수정 폼 활성화 (이미 입력폼에 값이 세팅됨)
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemberManager()
    window.show()
    sys.exit(app.exec_())
