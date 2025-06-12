def get_recommendation(skin_type):
    recs = {
        "dry": [
            "Moisturizer berbahan hyaluronic acid",
            "Hindari sabun wajah yang mengandung alkohol",
            "Gunakan hydrating toner"
        ],
        "oily": [
            "Gunakan cleanser berbahan salicylic acid",
            "Pilih moisturizer ringan berbahan gel",
            "Gunakan clay mask seminggu sekali"
        ],
        "normal": [
            "Gunakan gentle cleanser",
            "Pelembap ringan berbahan air",
            "Rutin menggunakan sunscreen"
        ]
    }
    return recs.get(skin_type, [])