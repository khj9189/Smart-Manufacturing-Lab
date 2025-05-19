# from flask import Flask, jsonify
# from basyx.aas import model, adapter
# from basyx.aas.adapter import aasx

# import os

# app = Flask(__name__)
# object_store = model.DictObjectStore()
# file_store = aasx.DictSupplementaryFileContainer()  # ✅ 추가

# # AASX 경로
# aasx_path = os.path.join(os.path.dirname(__file__), "storage", "01_Festo.aasx")

# # AASX 로드
# with aasx.AASXReader(aasx_path) as reader:
#     reader.read_into(object_store=object_store, file_store=file_store)  # ✅ 수정됨

# @app.route("/shells", methods=["GET"])
# def get_shells():
#     shells = []
#     for obj in object_store:
#         if isinstance(obj, model.AssetAdministrationShell):
#             shells.append({
#                 "id": {
#                     "type": "IRI",
#                     "value": obj.id
#                 },
#                 "idShort": obj.id_short
#             })
#     return jsonify(shells)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)





from flask import Flask, jsonify
from main import exported_object_store as object_store  # ✅ main.py에서 AASX object store 불러오기
from basyx.aas import model

app = Flask(__name__)

@app.route("/calculate", methods=["GET"])
def calculate():
    print("=== Submodel Elements ===")

    value_a = None
    value_b = None

    for obj in object_store:
        if not isinstance(obj, model.AssetAdministrationShell):
            continue

        for sm_ref in obj.submodel:
            try:
                submodel_key = sm_ref.keys[0].value.strip()
            except AttributeError:
                submodel_key = str(sm_ref).strip()

            submodel = None
            for o in object_store:
                if isinstance(o, model.Submodel):
                    real_id = getattr(o.id, 'id', o.id).strip()  # ✅ .strip() 추가
                    print(f"🔍 Checking Submodel: {real_id} vs {submodel_key}")
                    print(f"[DEBUG] Equal? {real_id == submodel_key}")
                    if real_id == submodel_key:
                        submodel = o
                        break


            if submodel is None:
                print(f"❌ Submodel {submodel_key} not found in store")
                continue

            print(f"✅ Submodel found: {submodel.id_short}")

            # Submodel 내부 요소 확인
            for elem in submodel.submodel_element:
                print(f"  ➜ Element: {elem.id_short}, value: {getattr(elem, 'value', None)}")
                if elem.id_short == "a":
                    value_a = int(elem.value)
                elif elem.id_short == "b":
                    value_b = int(elem.value)

    if value_a is None or value_b is None:
        return jsonify({"error": "a or b not found"}), 400

    return jsonify({
        "a": value_a,
        "b": value_b,
        "sum": value_a + value_b
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

