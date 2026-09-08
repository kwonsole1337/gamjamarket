from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from extensions import db
from models import Town, User, Product, Favorite, Chat, ChatMessage, Purchase, Payment

TOWNS = [
    {"name": "서면", "city": "부산광역시 부산진구", "lat": 35.1579, "lng": 129.0593, "radius": 1500},
    {"name": "해운대동", "city": "부산광역시 해운대구", "lat": 35.1631, "lng": 129.1635, "radius": 1500},
    {"name": "광안동", "city": "부산광역시 수영구", "lat": 35.1532, "lng": 129.1186, "radius": 1500},
    {"name": "남포동", "city": "부산광역시 중구", "lat": 35.0979, "lng": 129.0306, "radius": 1500},
    {"name": "온천동", "city": "부산광역시 동래구", "lat": 35.2048, "lng": 129.0778, "radius": 1500},
    {"name": "대연동", "city": "부산광역시 남구", "lat": 35.1334, "lng": 129.0972, "radius": 1500},
]

USERS = [
    {"username": "gamja_kim", "password": "kimchi2024!", "nickname": "김감자",
     "phone": "010-1111-2222", "emoji": "🥔", "town": "서면", "manner": 42.3},
    {"username": "potato_lee", "password": "leePotato!7", "nickname": "이감자",
     "phone": "010-2222-3333", "emoji": "🥔", "town": "남포동", "manner": 38.7},
    {"username": "sweet_park", "password": "sweetPark#9", "nickname": "박고구마",
     "phone": "010-3333-4444", "emoji": "🍠", "town": "광안동", "manner": 45.1},
    {"username": "yam_choi", "password": "yamChoi2025", "nickname": "최자색고구마",
     "phone": "010-4444-5555", "emoji": "🍠", "town": "해운대동", "manner": 36.9},
    {"username": "taro_jung", "password": "taroJung!3", "nickname": "정타로",
     "phone": "010-5555-6666", "emoji": "🥔", "town": "온천동", "manner": 39.4},
]

PRODUCTS = [
    {"title": "아이폰 13 프로 256GB 팝니다", "category": "디지털기기", "seller": "gamja_kim",
     "price": 750000, "trade": "직거래", "town": "서면", "status": "판매중", "views": 34,
     "desc": "작년에 구매해서 케이스 씌워서 깨끗하게 썼어요. 배터리 효율 89%입니다. 직거래 선호해요."},
    {"title": "맥북 에어 M1 8/256", "category": "디지털기기", "seller": "yam_choi",
     "price": 850000, "trade": "직거래", "town": "해운대동", "status": "판매중", "views": 41,
     "desc": "충전 사이클 120회, 사용감 거의 없습니다. 박스/충전기 포함."},
    {"title": "갤럭시 탭 S8 + 키보드커버", "category": "디지털기기", "seller": "taro_jung",
     "price": 350000, "trade": "택배", "town": "온천동", "status": "판매중", "views": 18,
     "desc": "필기용으로 쓰던 태블릿이에요. 스크래치 거의 없어요. 키보드 커버 같이 드립니다."},

    {"title": "3인용 패브릭 소파 (그레이)", "category": "가구/인테리어", "seller": "potato_lee",
     "price": 150000, "trade": "직거래", "town": "남포동", "status": "판매중", "views": 12,
     "desc": "이사가면서 급처합니다. 사용감 약간 있지만 상태 좋아요. 직접 보러오시면 좋아요."},
    {"title": "원목 책상 + 의자 세트", "category": "가구/인테리어", "seller": "taro_jung",
     "price": 65000, "trade": "직거래", "town": "온천동", "status": "판매중", "views": 5,
     "desc": "자취방에서 쓰던 책상/의자 세트입니다. 튼튼해요."},
    {"title": "협탁 2개 세트", "category": "가구/인테리어", "seller": "sweet_park",
     "price": 25000, "trade": "직거래", "town": "광안동", "status": "거래완료", "views": 9,
     "desc": "침대 옆에 두고 쓰던 협탁 2개입니다. 색상 화이트예요."},

    {"title": "나이키 에어포스1 265 새제품급", "category": "의류", "seller": "sweet_park",
     "price": 60000, "trade": "택배", "town": "광안동", "status": "판매중", "views": 21,
     "desc": "한 번밖에 안 신었어요. 사이즈 안 맞아서 팝니다. 박스 있습니다."},
    {"title": "여성 롱패딩 M 사이즈", "category": "의류", "seller": "gamja_kim",
     "price": 55000, "trade": "택배", "town": "서면", "status": "예약중", "views": 19,
     "desc": "작년에 사서 몇 번 안 입었어요. 깨끗합니다."},
    {"title": "유니클로 히트텍 5장 세트", "category": "의류", "seller": "potato_lee",
     "price": 15000, "trade": "택배", "town": "남포동", "status": "판매중", "views": 7,
     "desc": "사이즈가 안 맞아서 몇 번 안 입고 팝니다. 새 것 같아요."},

    {"title": "LG 트롬 세탁기 12kg", "category": "생활가전", "seller": "yam_choi",
     "price": 280000, "trade": "직거래", "town": "해운대동", "status": "판매중", "views": 8,
     "desc": "2년 사용, 정상 작동합니다. 자취방 정리하면서 팝니다."},
    {"title": "다이슨 무선청소기 V8", "category": "생활가전", "seller": "sweet_park",
     "price": 220000, "trade": "직거래", "town": "광안동", "status": "판매중", "views": 27,
     "desc": "흡입력 그대로예요. 헤드 2종 포함입니다."},
    {"title": "전자레인지 (삼성)", "category": "생활가전", "seller": "yam_choi",
     "price": 30000, "trade": "직거래", "town": "해운대동", "status": "판매중", "views": 4,
     "desc": "자취 정리하며 팝니다. 잘 작동해요."},

    {"title": "유모차 (거의 새것)", "category": "유아동", "seller": "taro_jung",
     "price": 90000, "trade": "직거래", "town": "온천동", "status": "판매중", "views": 15,
     "desc": "아이가 커서 몇 번 안 썼어요. 접이식이라 보관 편해요."},
    {"title": "아기 옷 모음 (개월수 다양)", "category": "유아동", "seller": "potato_lee",
     "price": 20000, "trade": "직거래", "town": "남포동", "status": "판매중", "views": 7,
     "desc": "한 박스 가득이에요. 세탁 완료했습니다."},
    {"title": "유아용 원목 식탁의자", "category": "유아동", "seller": "gamja_kim",
     "price": 35000, "trade": "직거래", "town": "서면", "status": "판매중", "views": 6,
     "desc": "아이 밥 먹일 때 쓰던 식탁의자예요. 흠집 약간 있어요."},

    {"title": "해리포터 전권 세트", "category": "도서", "seller": "gamja_kim",
     "price": 45000, "trade": "택배", "town": "서면", "status": "판매중", "views": 6,
     "desc": "전권 있습니다. 상태 아주 좋아요. 소장하실 분!"},
    {"title": "어린이 그림책 전집", "category": "도서", "seller": "taro_jung",
     "price": 35000, "trade": "택배", "town": "온천동", "status": "판매중", "views": 10,
     "desc": "아이가 다 커서 팝니다. 상태 좋아요."},
    {"title": "정보처리기사 수험서 세트", "category": "도서", "seller": "yam_choi",
     "price": 20000, "trade": "택배", "town": "해운대동", "status": "판매중", "views": 13,
     "desc": "올해 딴 시험 교재입니다. 필기 거의 없어요."},

    {"title": "캠핑 텐트 4인용", "category": "스포츠/레저", "seller": "potato_lee",
     "price": 70000, "trade": "직거래", "town": "남포동", "status": "판매중", "views": 9,
     "desc": "작년 여름에 두 번 사용했어요. 폴대 이상 없습니다."},
    {"title": "골프채 풀세트 (초보용)", "category": "스포츠/레저", "seller": "sweet_park",
     "price": 300000, "trade": "직거래", "town": "광안동", "status": "판매중", "views": 13,
     "desc": "입문용으로 좋아요. 가방 포함입니다."},
    {"title": "하이브리드 자전거 26인치", "category": "스포츠/레저", "seller": "gamja_kim",
     "price": 120000, "trade": "직거래", "town": "서면", "status": "판매중", "views": 22,
     "desc": "출퇴근용으로 타던 자전거예요. 타이어 최근 교체했습니다."},

    {"title": "강아지 하우스 (중형견용)", "category": "기타", "seller": "taro_jung",
     "price": 18000, "trade": "직거래", "town": "온천동", "status": "판매중", "views": 3,
     "desc": "강아지가 안 들어가서 팝니다. 거의 새 제품이에요."},
    {"title": "캠핑용 랜턴 2개", "category": "기타", "seller": "potato_lee",
     "price": 12000, "trade": "직거래", "town": "남포동", "status": "판매중", "views": 2,
     "desc": "밝기 좋아요. 건전지 포함해서 드려요."},
    {"title": "미개봉 명절 선물세트", "category": "기타", "seller": "sweet_park",
     "price": 40000, "trade": "직거래", "town": "광안동", "status": "판매중", "views": 11,
     "desc": "선물 받았는데 안 먹는 거라 팝니다. 미개봉이에요."},
]

def run_seed():
    if User.query.first() is not None:
        print("[gamjamarket] 이미 데이터가 있어 시드를 건너뜁니다.")
        return

    print("[gamjamarket] 시드 데이터 생성을 시작합니다...")
    now = datetime.utcnow()

    towns = {}
    for t in TOWNS:
        town = Town(name=t["name"], city=t["city"], center_lat=t["lat"],
                    center_lng=t["lng"], radius_m=t["radius"])
        db.session.add(town)
        towns[t["name"]] = town
    db.session.flush()

    users = {}
    for u in USERS:
        town = towns[u["town"]]
        user = User(
            username=u["username"],
            password_hash=generate_password_hash(u["password"]),
            nickname=u["nickname"],
            phone=u["phone"],
            profile_emoji=u["emoji"],
            verified_town_id=town.id,
            verified_lat=town.center_lat,
            verified_lng=town.center_lng,
            verified_at=now,
            manner_score=u["manner"],
        )
        db.session.add(user)
        users[u["username"]] = user
    db.session.flush()

    products = {}
    for i, p in enumerate(PRODUCTS):
        product = Product(
            seller_id=users[p["seller"]].id,
            title=p["title"],
            category=p["category"],
            description=p["desc"],
            price=p["price"],
            trade_type=p["trade"],
            town_name=p["town"],
            status=p["status"],
            view_count=p["views"],
            created_at=now - timedelta(hours=len(PRODUCTS) - i),
        )
        db.session.add(product)
        products[p["title"]] = product
    db.session.flush()

    favorites = [
        ("potato_lee", "아이폰 13 프로 256GB 팝니다"),
        ("gamja_kim", "다이슨 무선청소기 V8"),
        ("taro_jung", "맥북 에어 M1 8/256"),
    ]
    for username, title in favorites:
        db.session.add(Favorite(user_id=users[username].id, product_id=products[title].id))

    chat_defs = [
        {
            "product": "아이폰 13 프로 256GB 팝니다", "buyer": "potato_lee", "seller": "gamja_kim",
            "address": "부산 부산진구 서면로68번길 12 감자하이츠 305호", "phone": "010-1111-2222",
            "messages": [
                ("potato_lee", "안녕하세요! 아이폰 아직 판매중인가요?"),
                ("gamja_kim", "네 아직 있어요~ 직거래 가능하세요?"),
                ("potato_lee", "네 가능합니다! 주소 좀 알려주세요"),
                ("gamja_kim", "📍 위치와 연락처를 공유했습니다: 부산 부산진구 서면로68번길 12 감자하이츠 305호 / 010-1111-2222"),
            ],
        },
        {
            "product": "LG 트롬 세탁기 12kg", "buyer": "taro_jung", "seller": "yam_choi",
            "address": "부산 해운대구 해운대해변로 220 고구마오션뷰 1701호", "phone": "010-4444-5555",
            "messages": [
                ("taro_jung", "세탁기 상태 어떤가요?"),
                ("yam_choi", "2년 썼는데 상태 좋아요! 직접 보러 오실래요?"),
                ("yam_choi", "📍 위치와 연락처를 공유했습니다: 부산 해운대구 해운대해변로 220 고구마오션뷰 1701호 / 010-4444-5555"),
            ],
        },
        {
            "product": "다이슨 무선청소기 V8", "buyer": "gamja_kim", "seller": "sweet_park",
            "address": "부산 수영구 광안해변로 55 고구마타워 8층", "phone": "010-3333-4444",
            "messages": [
                ("gamja_kim", "청소기 헤드 다 있나요?"),
                ("sweet_park", "네 2종 다 있어요!"),
                ("sweet_park", "📍 위치와 연락처를 공유했습니다: 부산 수영구 광안해변로 55 고구마타워 8층 / 010-3333-4444"),
            ],
        },
        {
            "product": "맥북 에어 M1 8/256", "buyer": "sweet_park", "seller": "yam_choi",
            "address": None, "phone": None,
            "messages": [
                ("sweet_park", "맥북 가격 조금만 깎아주실 수 있나요?"),
                ("yam_choi", "음... 82만원까지는 가능해요!"),
                ("sweet_park", "생각해볼게요 감사합니다"),
            ],
        },
    ]

    for c in chat_defs:
        chat = Chat(
            product_id=products[c["product"]].id,
            buyer_id=users[c["buyer"]].id,
            seller_id=users[c["seller"]].id,
            shared_address=c["address"],
            shared_phone=c["phone"],
        )
        db.session.add(chat)
        db.session.flush()
        for sender, msg in c["messages"]:
            db.session.add(ChatMessage(chat_id=chat.id, sender_id=users[sender].id, message=msg))

    target_product = products["여성 롱패딩 M 사이즈"]
    purchase = Purchase(
        product_id=target_product.id,
        buyer_id=users["potato_lee"].id,
        seller_id=users["gamja_kim"].id,
        amount=target_product.price,
        status="결제완료",
    )
    db.session.add(purchase)
    db.session.flush()
    db.session.add(Payment(purchase_id=purchase.id, amount=target_product.price, status="결제완료"))

    db.session.commit()
    print(f"[gamjamarket] 시드 완료: 동네 {len(TOWNS)}개, 사용자 {len(USERS)}명, "
          f"상품 {len(PRODUCTS)}개, 채팅방 {len(chat_defs)}개")
