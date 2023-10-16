import tempfile
import traceback
from importlib import util
from flask import Flask, jsonify, render_template, request
import python2verilog
from python2verilog.api.namespace import get_namespace, namespace_to_verilog


app = Flask(__name__)


@app.route("/")
def index():
    try:
        print(f"{python2verilog.__name__} {python2verilog.__version__}")
    except Exception:
        pass
    return render_template("index.html")


def parse(raw: str) -> tuple[str, int]:
    """
    :return: (result, error)
    """
    raw = "from python2verilog import verilogify\n" + raw

    # Create a temporary source code file
    with tempfile.NamedTemporaryFile(suffix=".py") as tmp:
        tmp.write(raw.encode())
        tmp.flush()

        error = False
        try:
            spec = util.spec_from_file_location("tmp", tmp.name)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)

            ns = get_namespace(tmp.name)
            result, _ = namespace_to_verilog(ns)
        except Exception:
            error = True
            result = traceback.format_exc(limit=1)
            print(traceback.format_exc())
        finally:
            return result, int(error)


@app.route("/api/update", methods=["POST"])
def parse_py():
    text = request.form["text"]
    result, err = parse(text)
    return jsonify({"result": result, "error": err})
