import ROOT

def test_tgraph():
    g = ROOT.TGraph()
    g.SetPoint(0, 1, 2)
    assert g.GetN() == 1
