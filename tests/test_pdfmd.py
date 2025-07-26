import sys
import types

from batchsmith import pdfmd


def _setup_pypandoc(monkeypatch, calls):
    mod = types.ModuleType("pypandoc")

    def dummy_convert_file(input_path, fmt, outputfile=None, extra_args=None):
        calls["args"] = {
            "input_path": input_path,
            "fmt": fmt,
            "outputfile": outputfile,
            "extra_args": extra_args,
        }

    mod.convert_file = dummy_convert_file
    monkeypatch.setitem(sys.modules, "pypandoc", mod)


def test_convert_md_to_pdf(monkeypatch, tmp_path):
    md_file = tmp_path / "doc.md"
    md_file.write_text("# hi")
    calls = {}
    _setup_pypandoc(monkeypatch, calls)

    out = tmp_path / "out.pdf"
    pdfmd.convert(str(md_file), str(out))

    assert calls["args"]["fmt"] == "pdf"
    assert calls["args"]["outputfile"] == str(out)
    assert "--pdf-engine=xelatex" in calls["args"]["extra_args"]


def test_convert_pdf_to_md(monkeypatch, tmp_path):
    pdf_file = tmp_path / "doc.pdf"
    pdf_file.write_text("binary")
    calls = {}
    _setup_pypandoc(monkeypatch, calls)

    out = tmp_path / "out.md"
    pdfmd.convert(str(pdf_file), str(out))

    assert calls["args"]["fmt"] == "md"
    assert calls["args"]["outputfile"] == str(out)
