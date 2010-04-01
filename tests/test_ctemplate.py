from tests import TemplateTest

from ptemplate import CTemplate

class TestCTemplate(TemplateTest):
    cls = CTemplate

    def test_basic(self):
        self.assertProduces("{{foo}}", "bar", {"foo": "bar"})

    # The following are ported from Google's template_unittest.cc,
    # starting around line 400.
    def test_weird_syntax(self):
        # XXX
        #self.assertProduces("hi {{{! VAR {{!VAR} }} lo", "hi { lo")

        self.assertProduces("fn(){{{BI_NEWLINE}} x=4;{{BI_NEWLINE}}}",
            "fn(){\n x=4;\n}")

        # XXX
        #self.assertProduces("{{{{{{VAR}}}}}}}}", "{{{{}}}}}}")

    def test_comment(self):
        self.assertProduces("hi {{!VAR}} lo", "hi  lo")
        self.assertProduces("hi {{!VAR {VAR} }} lo", "hi  lo")
        # XXX
        #self.assertProduces("hi {{! VAR {{!VAR} }} lo", "hi  lo")

    # Skipping TestSetMarkerDelimiters; no plans to support that feature.

    def test_variable(self):
        data = {}
        input = "hi {{VAR}} lo"
        self.assertProduces(input, "hi  lo", data)
