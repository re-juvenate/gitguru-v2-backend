```python -m src.sast.ex```

response:
```json
{
  "errors": [],
  "paths": {
    "scanned": [
      "jsonnet.js"
    ]
  },
  "results": [
    {
      "check_id": "javascript.browser.security.eval-detected.eval-detected",
      "end": {
        "col": 44,
        "line": 39,
        "offset": 1015
      },
      "extra": {
        "engine_kind": "OSS",
        "fingerprint": "requires login",
        "lines": "requires login",
        "message": "Detected the use of eval(). eval() can be dangerous if used to evaluate dynamic content. If this content can be input from outside the program, this may be a code injection vulnerability. Ensure evaluated content is not definable by external sources.",
        "metadata": {
          "asvs": {
            "control_id": "5.2.4 Dynamic Code Execution Features",
            "control_url": "https://github.com/OWASP/ASVS/blob/master/4.0/en/0x13-V5-Validation-Sanitization-Encoding.md#v52-sanitization-and-sandboxing",
            "section": "V5 Validation, Sanitization and Encoding",
            "version": "4"
          },
          "category": "security",
          "confidence": "LOW",
          "cwe": [
            "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')"
          ],
          "impact": "MEDIUM",
          "license": "Semgrep Rules License v1.0. For more details, visit semgrep.dev/legal/rules-license",
          "likelihood": "LOW",
          "owasp": [
            "A03:2021 - Injection"
          ],
          "references": [
            "https://owasp.org/Top10/A03_2021-Injection"
          ],
          "shortlink": "https://sg.run/7ope",
          "source": "https://semgrep.dev/r/javascript.browser.security.eval-detected.eval-detected",
          "subcategory": [
            "audit"
          ],
          "technology": [
            "browser"
          ],
          "vulnerability_class": [
            "Code Injection"
          ]
        },
        "severity": "WARNING",
        "validation_state": "NO_VALIDATOR"
      },
      "path": "jsonnet.js",
      "start": {
        "col": 34,
        "line": 39,
        "offset": 1005
      }
    },
    {
      "check_id": "javascript.browser.security.eval-detected.eval-detected",
      "end": {
        "col": 44,
        "line": 44,
        "offset": 1207
      },
      "extra": {
        "engine_kind": "OSS",
        "fingerprint": "requires login",
        "lines": "requires login",
        "message": "Detected the use of eval(). eval() can be dangerous if used to evaluate dynamic content. If this content can be input from outside the program, this may be a code injection vulnerability. Ensure evaluated content is not definable by external sources.",
        "metadata": {
          "asvs": {
            "control_id": "5.2.4 Dynamic Code Execution Features",
            "control_url": "https://github.com/OWASP/ASVS/blob/master/4.0/en/0x13-V5-Validation-Sanitization-Encoding.md#v52-sanitization-and-sandboxing",
            "section": "V5 Validation, Sanitization and Encoding",
            "version": "4"
          },
          "category": "security",
          "confidence": "LOW",
          "cwe": [
            "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')"
          ],
          "impact": "MEDIUM",
          "license": "Semgrep Rules License v1.0. For more details, visit semgrep.dev/legal/rules-license",
          "likelihood": "LOW",
          "owasp": [
            "A03:2021 - Injection"
          ],
          "references": [
            "https://owasp.org/Top10/A03_2021-Injection"
          ],
          "shortlink": "https://sg.run/7ope",
          "source": "https://semgrep.dev/r/javascript.browser.security.eval-detected.eval-detected",
          "subcategory": [
            "audit"
          ],
          "technology": [
            "browser"
          ],
          "vulnerability_class": [
            "Code Injection"
          ]
        },
        "severity": "WARNING",
        "validation_state": "NO_VALIDATOR"
      },
      "path": "jsonnet.js",
      "start": {
        "col": 34,
        "line": 44,
        "offset": 1197
      }
    },
    {
      "check_id": "javascript.browser.security.eval-detected.eval-detected",
      "end": {
        "col": 54,
        "line": 95,
        "offset": 2698
      },
      "extra": {
        "engine_kind": "OSS",
        "fingerprint": "requires login",
        "lines": "requires login",
        "message": "Detected the use of eval(). eval() can be dangerous if used to evaluate dynamic content. If this content can be input from outside the program, this may be a code injection vulnerability. Ensure evaluated content is not definable by external sources.",
        "metadata": {
          "asvs": {
            "control_id": "5.2.4 Dynamic Code Execution Features",
            "control_url": "https://github.com/OWASP/ASVS/blob/master/4.0/en/0x13-V5-Validation-Sanitization-Encoding.md#v52-sanitization-and-sandboxing",
            "section": "V5 Validation, Sanitization and Encoding",
            "version": "4"
          },
          "category": "security",
          "confidence": "LOW",
          "cwe": [
            "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')"
          ],
          "impact": "MEDIUM",
          "license": "Semgrep Rules License v1.0. For more details, visit semgrep.dev/legal/rules-license",
          "likelihood": "LOW",
          "owasp": [
            "A03:2021 - Injection"
          ],
          "references": [
            "https://owasp.org/Top10/A03_2021-Injection"
          ],
          "shortlink": "https://sg.run/7ope",
          "source": "https://semgrep.dev/r/javascript.browser.security.eval-detected.eval-detected",
          "subcategory": [
            "audit"
          ],
          "technology": [
            "browser"
          ],
          "vulnerability_class": [
            "Code Injection"
          ]
        },
        "severity": "WARNING",
        "validation_state": "NO_VALIDATOR"
      },
      "path": "jsonnet.js",
      "start": {
        "col": 44,
        "line": 95,
        "offset": 2688
      }
    },
    {
      "check_id": "javascript.browser.security.eval-detected.eval-detected",
      "end": {
        "col": 54,
        "line": 100,
        "offset": 2927
      },
      "extra": {
        "engine_kind": "OSS",
        "fingerprint": "requires login",
        "lines": "requires login",
        "message": "Detected the use of eval(). eval() can be dangerous if used to evaluate dynamic content. If this content can be input from outside the program, this may be a code injection vulnerability. Ensure evaluated content is not definable by external sources.",
        "metadata": {
          "asvs": {
            "control_id": "5.2.4 Dynamic Code Execution Features",
            "control_url": "https://github.com/OWASP/ASVS/blob/master/4.0/en/0x13-V5-Validation-Sanitization-Encoding.md#v52-sanitization-and-sandboxing",
            "section": "V5 Validation, Sanitization and Encoding",
            "version": "4"
          },
          "category": "security",
          "confidence": "LOW",
          "cwe": [
            "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')"
          ],
          "impact": "MEDIUM",
          "license": "Semgrep Rules License v1.0. For more details, visit semgrep.dev/legal/rules-license",
          "likelihood": "LOW",
          "owasp": [
            "A03:2021 - Injection"
          ],
          "references": [
            "https://owasp.org/Top10/A03_2021-Injection"
          ],
          "shortlink": "https://sg.run/7ope",
          "source": "https://semgrep.dev/r/javascript.browser.security.eval-detected.eval-detected",
          "subcategory": [
            "audit"
          ],
          "technology": [
            "browser"
          ],
          "vulnerability_class": [
            "Code Injection"
          ]
        },
        "severity": "WARNING",
        "validation_state": "NO_VALIDATOR"
      },
      "path": "jsonnet.js",
      "start": {
        "col": 44,
        "line": 100,
        "offset": 2917
      }
    },
    {
      "check_id": "javascript.browser.security.eval-detected.eval-detected",
      "end": {
        "col": 48,
        "line": 109,
        "offset": 3280
      },
      "extra": {
        "engine_kind": "OSS",
        "fingerprint": "requires login",
        "lines": "requires login",
        "message": "Detected the use of eval(). eval() can be dangerous if used to evaluate dynamic content. If this content can be input from outside the program, this may be a code injection vulnerability. Ensure evaluated content is not definable by external sources.",
        "metadata": {
          "asvs": {
            "control_id": "5.2.4 Dynamic Code Execution Features",
            "control_url": "https://github.com/OWASP/ASVS/blob/master/4.0/en/0x13-V5-Validation-Sanitization-Encoding.md#v52-sanitization-and-sandboxing",
            "section": "V5 Validation, Sanitization and Encoding",
            "version": "4"
          },
          "category": "security",
          "confidence": "LOW",
          "cwe": [
            "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')"
          ],
          "impact": "MEDIUM",
          "license": "Semgrep Rules License v1.0. For more details, visit semgrep.dev/legal/rules-license",
          "likelihood": "LOW",
          "owasp": [
            "A03:2021 - Injection"
          ],
          "references": [
            "https://owasp.org/Top10/A03_2021-Injection"
          ],
          "shortlink": "https://sg.run/7ope",
          "source": "https://semgrep.dev/r/javascript.browser.security.eval-detected.eval-detected",
          "subcategory": [
            "audit"
          ],
          "technology": [
            "browser"
          ],
          "vulnerability_class": [
            "Code Injection"
          ]
        },
        "severity": "WARNING",
        "validation_state": "NO_VALIDATOR"
      },
      "path": "jsonnet.js",
      "start": {
        "col": 38,
        "line": 109,
        "offset": 3270
      }
    },
    {
      "check_id": "javascript.browser.security.eval-detected.eval-detected",
      "end": {
        "col": 48,
        "line": 114,
        "offset": 3497
      },
      "extra": {
        "engine_kind": "OSS",
        "fingerprint": "requires login",
        "lines": "requires login",
        "message": "Detected the use of eval(). eval() can be dangerous if used to evaluate dynamic content. If this content can be input from outside the program, this may be a code injection vulnerability. Ensure evaluated content is not definable by external sources.",
        "metadata": {
          "asvs": {
            "control_id": "5.2.4 Dynamic Code Execution Features",
            "control_url": "https://github.com/OWASP/ASVS/blob/master/4.0/en/0x13-V5-Validation-Sanitization-Encoding.md#v52-sanitization-and-sandboxing",
            "section": "V5 Validation, Sanitization and Encoding",
            "version": "4"
          },
          "category": "security",
          "confidence": "LOW",
          "cwe": [
            "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')"
          ],
          "impact": "MEDIUM",
          "license": "Semgrep Rules License v1.0. For more details, visit semgrep.dev/legal/rules-license",
          "likelihood": "LOW",
          "owasp": [
            "A03:2021 - Injection"
          ],
          "references": [
            "https://owasp.org/Top10/A03_2021-Injection"
          ],
          "shortlink": "https://sg.run/7ope",
          "source": "https://semgrep.dev/r/javascript.browser.security.eval-detected.eval-detected",
          "subcategory": [
            "audit"
          ],
          "technology": [
            "browser"
          ],
          "vulnerability_class": [
            "Code Injection"
          ]
        },
        "severity": "WARNING",
        "validation_state": "NO_VALIDATOR"
      },
      "path": "jsonnet.js",
      "start": {
        "col": 38,
        "line": 114,
        "offset": 3487
      }
    }
  ],
  "skipped_rules": [],
  "version": "1.109.0"
}
```
