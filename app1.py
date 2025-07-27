from flask import Flask, request, jsonify

app = Flask(__name__)

# 임시 데이터 (DB 대신 파이썬 리스트 사용)
users = [
    {"id": 1, "name": "홍길동"},
    {"id": 2, "name": "이몽룡"}
]

# [GET] 모든 유저 조회
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

# [GET] 특정 유저 조회
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

# [POST] 유저 생성
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = {
        "id": users[-1]["id"] + 1 if users else 1,
        "name": data.get("name")
    }
    users.append(new_user)
    return jsonify(new_user), 201

# [PUT] 유저 정보 수정
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.json
    user["name"] = data.get("name", user["name"])
    return jsonify(user)

# [DELETE] 유저 삭제
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    users = [u for u in users if u["id"] != user_id]
    return jsonify({"result": "User deleted"})

if __name__ == '__main__':
    app.run(debug=True)
