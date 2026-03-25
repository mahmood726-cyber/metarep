"""
Selenium tests for MetaRep — Replication Probability from Meta-Analytic Evidence.
Usage: python -m pytest tests/test_metarep.py -v --timeout=60
"""
import sys, os, time, math, unittest
if __name__ == '__main__' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

HTML_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metarep.html'))
FILE_URL = 'file:///' + HTML_PATH.replace('\\', '/')

_WDM = os.path.expanduser('~/.wdm/drivers/chromedriver/win64')
_CACHED = []
if os.path.isdir(_WDM):
    for v in sorted(os.listdir(_WDM), reverse=True):
        for sub in ('chromedriver-win32', ''):
            c = os.path.join(_WDM, v, sub, 'chromedriver.exe').rstrip(os.sep)
            if os.path.isfile(c): _CACHED.append(c); break

def _driver():
    opts = ChromeOptions()
    opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-gpu'); opts.add_argument('--incognito'); opts.add_argument('--window-size=1280,900')
    opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    for p in _CACHED:
        try: return webdriver.Chrome(service=ChromeService(executable_path=p), options=opts)
        except WebDriverException: continue
    try: return webdriver.Chrome(options=opts)
    except WebDriverException: pass
    try:
        from selenium.webdriver.edge.options import Options as EO
        eo = EO(); eo.add_argument('--headless=new'); eo.add_argument('--no-sandbox')
        eo.add_argument('--disable-gpu'); eo.add_argument('--inprivate'); eo.add_argument('--window-size=1280,900')
        return webdriver.Edge(options=eo)
    except: pass
    raise WebDriverException('No driver')


class TestMetaRep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = _driver(); cls.d.set_page_load_timeout(30)
        cls.d.get(FILE_URL); time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        if cls.d:
            try:
                import threading; done = threading.Event()
                def q():
                    try: cls.d.quit()
                    except: pass
                    finally: done.set()
                threading.Thread(target=q, daemon=True).start()
                if not done.wait(10):
                    try: cls.d.service.process.kill()
                    except: pass
            except: pass

    def js(self, s): return self.d.execute_script(s)

    # 01: Page title
    def test_01_title(self):
        self.assertIn('MetaRep', self.d.title)

    # 02: Auto-compute on load
    def test_02_auto_compute(self):
        v = self.d.find_element(By.ID, 'repProb').text
        self.assertNotEqual(v, '—')
        self.assertIn('%', v)

    # 03: DAPA-HF replication probability should be very high (OR=0.74, tau2=0, large N)
    def test_03_dapahf_high_rep(self):
        p = self.js("return window._lastRep ? window._lastRep.pRep : null;")
        self.assertIsNotNone(p)
        self.assertGreater(p, 0.8, f'DAPA-HF rep prob should be >80%, got {p*100:.1f}%')

    # 04: Core formula correctness — manual calculation
    def test_04_formula_correctness(self):
        """P(rep) for theta=log(0.74), tau2=0, se_new=sqrt(2/2500), alpha=0.05"""
        result = self.js("""
            var theta = Math.log(0.74);
            var tau2 = 0;
            var seNew = Math.sqrt(2/2500);
            return repProb(theta, tau2, seNew, 0.05);
        """)
        # Manual: theta=-0.3012, z=1.96, seNew=0.02828
        # P = Phi((0.3012 - 1.96*0.02828) / sqrt(0 + 0.02828^2))
        # = Phi((0.3012 - 0.05543) / 0.02828)
        # = Phi(8.69) ≈ 1.0
        self.assertGreater(result, 0.99, f'Expected near 1.0, got {result}')

    # 05: Zero effect → P(rep) should be near 0
    def test_05_zero_effect(self):
        result = self.js("return repProb(0, 0, 0.1, 0.05);")
        self.assertLess(result, 0.03, f'P(rep) at theta=0 should be near 0, got {result}')

    # 06: Heterogeneity reduces replication probability
    def test_06_tau2_reduces_rep(self):
        r0 = self.js("return repProb(0.5, 0, 0.1, 0.05);")
        r1 = self.js("return repProb(0.5, 0.1, 0.1, 0.05);")
        self.assertGreater(r0, r1, f'tau2=0 ({r0:.3f}) should have higher rep prob than tau2=0.1 ({r1:.3f})')

    # 07: Larger sample → higher replication
    def test_07_larger_n_higher_rep(self):
        r_small = self.js("return repProb(0.3, 0.01, Math.sqrt(2/500), 0.05);")
        r_large = self.js("return repProb(0.3, 0.01, Math.sqrt(2/5000), 0.05);")
        self.assertGreater(r_large, r_small)

    # 08: Classical power >= predictive power
    def test_08_classical_ge_predictive(self):
        self.js("""
            document.getElementById('exSel').value = 'statins';
            document.getElementById('exSel').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        r = self.js("return window._lastRep;")
        self.assertGreaterEqual(r['pClassical'], r['pRep'],
            f'Classical ({r["pClassical"]:.3f}) should >= predictive ({r["pRep"]:.3f})')

    # 09: Load SSRI example
    def test_09_ssri_example(self):
        self.js("""
            document.getElementById('exSel').value = 'ssri';
            document.getElementById('exSel').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        p = self.js("return window._lastRep ? window._lastRep.pRep : null;")
        self.assertIsNotNone(p)
        # SSRIs have high tau2 relative to effect → moderate/low replication
        self.assertLess(p, 0.95, 'SSRIs with high heterogeneity should have <95% rep prob')

    # 10: Dark mode
    def test_10_dark_mode(self):
        self.d.find_element(By.ID, 'themeBtn').click()
        time.sleep(0.3)
        self.assertEqual(self.d.find_element(By.TAG_NAME, 'html').get_attribute('data-theme'), 'dark')
        self.d.find_element(By.ID, 'themeBtn').click()
        time.sleep(0.3)

    # 11: About modal
    def test_11_about_modal(self):
        self.d.find_element(By.ID, 'aboutBtn').click()
        time.sleep(0.3)
        m = self.d.find_element(By.ID, 'aboutModal')
        self.assertNotIn('hidden', m.get_attribute('class'))
        self.assertIn('Replication', m.text)
        self.d.find_element(By.ID, 'aboutX').click()
        time.sleep(0.3)
        self.assertIn('hidden', self.d.find_element(By.ID, 'aboutModal').get_attribute('class'))

    # 12: No console errors
    def test_12_no_console_errors(self):
        try: logs = self.d.get_log('browser')
        except: self.skipTest('No log support')
        severe = [e for e in logs if e.get('level') == 'SEVERE' and 'favicon' not in e.get('message','').lower()]
        if severe: self.fail(f'Console errors: {[e["message"] for e in severe]}')

    # 13: Chart rendered
    def test_13_chart_rendered(self):
        chart = self.d.find_element(By.ID, 'repCurve')
        svgs = chart.find_elements(By.CSS_SELECTOR, '.plot-container, svg')
        self.assertGreater(len(svgs), 0)

    # 14: Export function exists
    def test_14_export_exists(self):
        self.assertTrue(self.js("return typeof exportBundle === 'function'"))
        self.assertTrue(self.js("return typeof exportR === 'function'"))

    # 15: Skip-nav
    def test_15_skip_nav(self):
        skip = self.d.find_elements(By.CSS_SELECTOR, 'a[href="#main"]')
        self.assertEqual(len(skip), 1)

    # 16: CSP
    def test_16_csp(self):
        csp = self.js("var m = document.querySelector('meta[http-equiv=\"Content-Security-Policy\"]'); return m ? m.content : null;")
        self.assertIsNotNone(csp)
        self.assertIn('default-src', csp)

    # 17: aria-live on results
    def test_17_aria_live(self):
        self.assertEqual(self.d.find_element(By.ID, 'results').get_attribute('aria-live'), 'polite')

    # 18: Slider updates
    def test_18_slider(self):
        self.js("""
            document.getElementById('exSel').value = 'dapahf';
            document.getElementById('exSel').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.3)
        p1 = self.js("return window._lastRep.pRep;")
        self.js("""
            var s = document.getElementById('nNew'); s.value = '200';
            s.dispatchEvent(new Event('input'));
        """)
        time.sleep(0.3)
        p2 = self.js("return window._lastRep.pRep;")
        # Smaller sample → lower replication probability
        self.assertLess(p2, p1, f'N=200 ({p2:.3f}) should have lower rep than N=2500 ({p1:.3f})')

    # 19: Study table populated for examples
    def test_19_study_table(self):
        self.js("""
            document.getElementById('exSel').value = 'statins';
            document.getElementById('exSel').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        html = self.d.find_element(By.ID, 'studyTable').get_attribute('innerHTML')
        self.assertIn('WOSCOPS', html)
        self.assertIn('JUPITER', html)

    # 20: Gauge color classes
    def test_20_gauge_color(self):
        g = self.d.find_element(By.ID, 'gauge')
        c = g.get_attribute('class')
        self.assertTrue('high' in c or 'mod' in c or 'low' in c, f'Gauge needs color class, got: {c}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
