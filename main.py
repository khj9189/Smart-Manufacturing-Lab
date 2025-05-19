from flask import Flask, jsonify, request
from basyx.aas import model, adapter
from basyx.aas.adapter import aasx
import os

app = Flask(__name__)

# AAS 객체 불러오기
object_store = model.DictObjectStore()
file_store = aasx.DictSupplementaryFileContainer()

# AASX 파일 경로 설정
aasx_path = os.path.join(os.path.dirname(__file__), "storage", "01_Festo.aasx")

# AASX 파일 로딩
with aasx.AASXReader(aasx_path) as reader:
    reader.read_into(object_store=object_store, file_store=file_store)

@app.route("/calculate", methods=["GET"])
def calculate():
    print("=== Submodel Elements ===")
    value_a = None
    value_b = None

    for obj in object_store:
        if isinstance(obj, model.AssetAdministrationShell):
            for sm_ref in obj.submodel:
                try:
                    submodel_key = str(sm_ref.key[0].value).strip()
                except AttributeError:
                    submodel_key = str(sm_ref).strip()

                submodel = None

                for o in object_store:
                    if isinstance(o, model.Submodel):
                        real_id = str(getattr(o.id, 'id', o.id)).strip()
                        print(f"🔍 Checking Submodel: {real_id} vs {submodel_key}")
                        if real_id == submodel_key:
                            submodel = o
                            break

                if submodel is None:
                    print(f"❌ Submodel {submodel_key} not found in object_store")
                    continue

                print(f"✅ Found Submodel: {submodel.id_short}")
                for elem in submodel.submodel_element:
                    print(f"Element: {elem.id_short}, value: {getattr(elem, 'value', None)}")
                    if elem.id_short == "a":
                        value_a = int(elem.value)
                    elif elem.id_short == "b":
                        value_b = int(elem.value)

    if value_a is None or value_b is None:
        return jsonify({"error": "a or b not found"}), 400

    result = value_a + value_b
    return jsonify({
        "a": value_a,
        "b": value_b,
        "sum": result
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

