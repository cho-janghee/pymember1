import sys
import pymysql
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)

# === MySQL 연결 정보 ===
DB_HOST = 'localhost'
DB_USER = 'root'       # 본인 MySQL 사용자명
DB_PASSWORD = 'fris0819' # 본인 MySQL 비밀번호
DB_NAME = 'memberdb'

class MemberManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원정보 관리 프로그램 (MySQL)")
        self.setGeometry(300, 200, 600, 400)
        self.selected_id = None  # 현재 선택된 회원 ID

        # DB 연결
        self.conn = pymysql.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, charset='utf8mb4'
        )
        self.cur = self.conn.cursor()

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
        self.table = QTableWidget(0, 4)  # row 0, col 4 (id, 이름, 이메일, 나이)
        self.table.setHorizontalHeaderLabels(["ID", "이름", "이메일", "나이"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.cellClicked.connect(self.on_cell_clicked)

        # 레이아웃 정리
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.table)
        self.setCentralWidget(main_widget)

        self.update_table()

    def add_member(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        age = self.age_input.text().strip()
        if not (name and email and age):
            QMessageBox.warning(self, "경고", "모든 정보를 입력하세요.")
            return

        try:
            self.cur.execute(
                "INSERT INTO member (name, email, age) VALUES (%s, %s, %s)",
                (name, email, age)
            )
            self.conn.commit()
            self.update_table()
            self.clear_form()
        except pymysql.err.IntegrityError:
            QMessageBox.warning(self, "경고", "이미 등록된 이메일입니다.")
        except Exception as e:
            QMessageBox.warning(self, "DB 오류", str(e))

    def edit_member(self):
        if not self.selected_id:
            QMessageBox.warning(self, "경고", "수정할 회원을 선택하세요.")
            return
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        age = self.age_input.text().strip()
        if no
            .0t (name and email and age):
            QMessageBox.warning(self, "경고", "모든 정보를 입력하세요.")
            return

        try:
            self.cur.execute(
                "UPDATE member SET name=%s, email=%s, age=%s WHERE id=%s",
                (name, email, age, self.selected_id)
            )
            self.conn.commit()
            self.update_table()
            self.clear_form()
        except pymysql.err.IntegrityError:
            QMessageBox.warning(self, "경고", "이미 등록된 이메일입니다.")
        except Exception as e:
            QMessageBox.warning(self, "DB 오류", str(e))

    def delete_member(self):
        if not self.selected_id:
            QMessageBox.warning(self, "경고", "삭제할 회원을 선택하세요.")
            return

        confirm = QMessageBox.question(self, "확인", "정말 삭제하시겠습니까?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.cur.execute(
                    "DELETE FROM member WHERE id=%s", (self.selected_id,)
                )
                self.conn.commit()
                self.update_table()
                self.clear_form()
            except Exception as e:
                QMessageBox.warning(self, "DB 오류", str(e))

    def update_table(self):
        self.cur.execute("SELECT id, name, email, age FROM member ORDER BY id DESC")
        members = self.cur.fetchall()
        self.table.setRowCount(0)
        for row_idx, (mid, name, email, age) in enumerate(members):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(mid)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(email))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(age)))
        self.selected_id = None

    def clear_form(self):
        self.name_input.clear()
        self.email_input.clear()
        self.age_input.clear()
        self.table.clearSelection()
        self.selected_id = None

    def on_cell_clicked(self, row, column):
        # 표에서 한 줄 클릭하면 입력폼에 값 자동세팅
        self.selected_id = int(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        self.email_input.setText(self.table.item(row, 2).text())
        self.age_input.setText(self.table.item(row, 3).text())

    def closeEvent(self, event):
        self.cur.close()
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemberManager()
    window.show()
    sys.exit(app.exec_())
