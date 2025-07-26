members = []  # 회원 정보를 저장할 리스트

while True:
    print("\n===== 회원관리 프로그램 =====")
    print("1. 회원 등록")
    print("2. 회원 목록 보기")
    print("3. 종료")
    menu = input("메뉴 선택: ")

    if menu == "1":
        # 회원 등록
        name = input("이름: ")
        email = input("이메일: ")
        age = input("나이: ")
        # 회원 정보를 딕셔너리로 저장
        member = {"이름": name, "이메일": email, "나이": age}
        members.append(member)
        print("회원이 등록되었습니다.")
    elif menu == "2":
        # 회원 목록 출력
        print("\n=== 회원 목록 ===")
        for idx, m in enumerate(members, start=1):
            print(f"{idx}. 이름: {m['이름']}, 이메일: {m['이메일']}, 나이: {m['나이']}")
        if not members:
            print("등록된 회원이 없습니다.")
    elif menu == "3":
        print("프로그램을 종료합니다.")
        break
    else:
        print("잘못된 메뉴입니다. 다시 선택하세요.")

