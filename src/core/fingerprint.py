import random
import json

class FingerprintGenerator:
    @staticmethod
    def generate_fingerprint():
        """Generate a random, realistic browser fingerprint"""
        return {
            'userAgent': FingerprintGenerator._generate_user_agent(),
            'screen': FingerprintGenerator._generate_screen_metrics(),
            'navigator': FingerprintGenerator._generate_navigator(),
            'plugins': FingerprintGenerator._generate_plugins(),
            'webgl': FingerprintGenerator._generate_webgl(),
            'canvas': FingerprintGenerator._generate_canvas_noise()
        }

    @staticmethod
    def _generate_user_agent():
        chrome_versions = ['108.0.0.0', '109.0.0.0', '110.0.0.0', '111.0.0.0']
        os_versions = {
            'Windows': ['10.0', '11.0'],
            'Macintosh': ['10_15_7', '11_0_0', '12_0_0'],
            'Linux': ['x86_64', 'aarch64']
        }
        
        platform = random.choice(list(os_versions.keys()))
        os_version = random.choice(os_versions[platform])
        chrome_version = random.choice(chrome_versions)
        
        return f"Mozilla/5.0 ({platform}; {os_version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"

    @staticmethod
    def _generate_screen_metrics():
        resolutions = [
            (1920, 1080), (2560, 1440), (1366, 768),
            (1536, 864), (1440, 900), (1680, 1050)
        ]
        color_depths = [24, 30, 32]
        pixel_ratios = [1, 1.25, 1.5, 2]
        
        width, height = random.choice(resolutions)
        return {
            'width': width,
            'height': height,
            'availWidth': width - random.randint(0, 20),
            'availHeight': height - random.randint(30, 80),
            'colorDepth': random.choice(color_depths),
            'pixelDepth': random.choice(color_depths),
            'devicePixelRatio': random.choice(pixel_ratios)
        }

    @staticmethod
    def _generate_navigator():
        languages = [
            ['en-US', 'en'], ['en-GB', 'en'],
            ['fr-FR', 'fr', 'en'], ['de-DE', 'de', 'en'],
            ['es-ES', 'es', 'en']
        ]
        platforms = ['Win32', 'MacIntel', 'Linux x86_64']
        
        return {
            'language': random.choice(languages)[0],
            'languages': random.choice(languages),
            'platform': random.choice(platforms),
            'hardwareConcurrency': random.choice([2, 4, 6, 8, 12, 16]),
            'deviceMemory': random.choice([2, 4, 8, 16]),
            'maxTouchPoints': random.choice([0, 1, 2, 5]),
            'webdriver': 'undefined'
        }

    @staticmethod
    def _generate_plugins():
        plugins = [
            {'name': 'Chrome PDF Plugin', 'filename': 'internal-pdf-viewer'},
            {'name': 'Chrome PDF Viewer', 'filename': 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
            {'name': 'Native Client', 'filename': 'internal-nacl-plugin'}
        ]
        # Randomly remove some plugins
        return random.sample(plugins, random.randint(2, len(plugins)))

    @staticmethod
    def _generate_webgl():
        vendors = [
            'Google Inc. (NVIDIA)',
            'Intel Inc.',
            'AMD',
            'Apple GPU'
        ]
        renderers = [
            'ANGLE (NVIDIA GeForce RTX 2060 Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (AMD Radeon RX 5700 XT Direct3D11 vs_5_0 ps_5_0)',
            'Apple M1'
        ]
        return {
            'vendor': random.choice(vendors),
            'renderer': random.choice(renderers)
        }

    @staticmethod
    def _generate_canvas_noise():
        return {
            'noise': random.uniform(0.1, 0.4),
            'subtle': bool(random.getrandbits(1))
        }

def inject_fingerprint(driver, fingerprint):
    """Inject the generated fingerprint into the browser"""
    js_code = f"""
    // Override navigator properties
    Object.defineProperty(navigator, 'hardwareConcurrency', {{
        get: () => {fingerprint['navigator']['hardwareConcurrency']}
    }});
    Object.defineProperty(navigator, 'deviceMemory', {{
        get: () => {fingerprint['navigator']['deviceMemory']}
    }});
    Object.defineProperty(navigator, 'platform', {{
        get: () => "{fingerprint['navigator']['platform']}"
    }});
    Object.defineProperty(navigator, 'languages', {{
        get: () => {json.dumps(fingerprint['navigator']['languages'])}
    }});

    // Override screen properties
    Object.defineProperty(screen, 'width', {{
        get: () => {fingerprint['screen']['width']}
    }});
    Object.defineProperty(screen, 'height', {{
        get: () => {fingerprint['screen']['height']}
    }});
    Object.defineProperty(screen, 'colorDepth', {{
        get: () => {fingerprint['screen']['colorDepth']}
    }});
    Object.defineProperty(window, 'devicePixelRatio', {{
        get: () => {fingerprint['screen']['devicePixelRatio']}
    }});

    // WebGL fingerprint
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {{
        if (parameter === 37445) {{
            return "{fingerprint['webgl']['vendor']}";
        }}
        if (parameter === 37446) {{
            return "{fingerprint['webgl']['renderer']}";
        }}
        return getParameter.apply(this, arguments);
    }};
    """
    
    driver.execute_script(js_code)

def generate_fingerprint():
    """Generate a complete fingerprint for browser simulation"""
    return FingerprintGenerator.generate_fingerprint()