# XML to JSON Converter
A robust, feature-rich Python utility for converting XML files to JSON format with extensive customization options and comprehensive error handling.

## 🌟 Features

- **Multiple conversion modes**: Single file, batch directory processing, or programmatic API
- **Flexible output options**: Pretty-printed or compact JSON, stdout support
- **Advanced XML handling**: Namespaces, mixed content, attributes, empty elements
- **Comprehensive error handling**: Detailed error messages and logging levels
- **Memory efficient**: Handles large XML files without excessive memory usage
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Python 3.6+ compatible**: Uses backward-compatible type hints

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Command Line Options](#command-line-options)
- [XML to JSON Conversion Rules](#xml-to-json-conversion-rules)
- [Advanced Features](#advanced-features)
- [Programmatic Usage](#programmatic-usage)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [License](#license)

## 🚀 Installation

### Method 1: Direct Download

1. Download the `xml2json.py` file
2. Make it executable (Unix/macOS):
   ```bash
   chmod +x xml2json.py
   ```

### Method 2: Clone Repository

```bash
git clone https://github.com/mogomo/xml2json-converter.git
cd xml2json-converter
```

### Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## ⚡ Quick Start

```bash
# Convert a single XML file
python3 xml2json.py input.xml

# Convert with custom output name
python3 xml2json.py input.xml output.json

# Batch convert all XML files in a directory
python3 xml2json.py -d /path/to/xml/files
```

## 📚 Usage Examples

### Basic Conversion

```bash
# Simple conversion
python3 xml2json.py sample.xml

# Output to stdout
python3 xml2json.py sample.xml -

# Quiet mode (only show errors)
python3 xml2json.py sample.xml -q
```

### Advanced Options

```bash
# Compact JSON (no indentation)
python3 xml2json.py sample.xml --compact

# Remove root element wrapper
python3 xml2json.py sample.xml --no-root

# Strip XML namespaces
python3 xml2json.py sample.xml --strip-namespaces

# Ignore mixed content text
python3 xml2json.py sample.xml --no-mixed-content

# Empty elements as null instead of {}
python3 xml2json.py sample.xml --empty-as-null
```

### Batch Processing

```bash
# Convert all XML files in directory
python3 xml2json.py -d /path/to/xml/files

# Batch convert with custom output directory
python3 xml2json.py -d /path/xml --output-dir /path/json

# Batch convert with custom options
python3 xml2json.py -d /path/xml --compact --strip-namespaces
```

### Logging and Debugging

```bash
# Verbose output
python3 xml2json.py sample.xml -v

# Quiet mode (errors only)
python3 xml2json.py sample.xml -q

# Combine with other options
python3 xml2json.py sample.xml --strip-namespaces -v
```

## 🛠️ Command Line Options

| Option | Description |
|--------|-------------|
| `input` | Input XML file or directory (with -d flag) |
| `output` | Output JSON file (use "-" for stdout) |
| `-d, --directory` | Batch convert all XML files in input directory |
| `--output-dir` | Output directory for batch conversion |
| `--no-root` | Do not preserve root element as top-level key |
| `--compact` | Generate compact JSON without indentation |
| `--strip-namespaces` | Remove XML namespaces from element and attribute names |
| `--no-mixed-content` | Do not preserve mixed content text |
| `--empty-as-null` | Represent empty XML elements as null instead of {} |
| `-v, --verbose` | Enable verbose logging |
| `-q, --quiet` | Suppress all output except errors |
| `--version` | Show version information |
| `-h, --help` | Show help message |

## 🔄 XML to JSON Conversion Rules

### Basic Elements

**XML:**
```xml
<root>Hello World</root>
```

**JSON:**
```json
{
  "root": "Hello World"
}
```

### Elements with Attributes

**XML:**
```xml
<root id="123" type="test">Content</root>
```

**JSON:**
```json
{
  "root": {
    "@id": "123",
    "@type": "test",
    "#text": "Content"
  }
}
```

### Multiple Elements with Same Tag

**XML:**
```xml
<root>
  <item>Item1</item>
  <item>Item2</item>
  <item>Item3</item>
</root>
```

**JSON:**
```json
{
  "root": {
    "item": ["Item1", "Item2", "Item3"]
  }
}
```

### Nested Elements

**XML:**
```xml
<root>
  <person>
    <name>John</name>
    <age>30</age>
  </person>
</root>
```

**JSON:**
```json
{
  "root": {
    "person": {
      "name": "John",
      "age": "30"
    }
  }
}
```

### Mixed Content

**XML:**
```xml
<root>
  Some text
  <child>Child content</child>
  More text
</root>
```

**JSON:**
```json
{
  "root": {
    "#text": "Some text More text",
    "child": "Child content"
  }
}
```

### Empty Elements

**XML:**
```xml
<root>
  <empty/>
  <also-empty></also-empty>
</root>
```

**JSON (default):**
```json
{
  "root": {
    "empty": {},
    "also-empty": {}
  }
}
```

**JSON (with --empty-as-null):**
```json
{
  "root": {
    "empty": null,
    "also-empty": null
  }
}
```

### XML Namespaces

**XML:**
```xml
<root xmlns:ns="http://example.com/namespace">
  <ns:element ns:attr="value">Content</ns:element>
</root>
```

**JSON (default - preserves namespaces):**
```json
{
  "root": {
    "{http://example.com/namespace}element": {
      "@{http://example.com/namespace}attr": "value",
      "#text": "Content"
    }
  }
}
```

**JSON (with --strip-namespaces):**
```json
{
  "root": {
    "element": {
      "@attr": "value",
      "#text": "Content"
    }
  }
}
```

## 🔧 Advanced Features

### Namespace Handling

The converter can handle XML namespaces in two ways:

1. **Preserve namespaces** (default): Full namespace URIs are included
2. **Strip namespaces** (`--strip-namespaces`): Only local names are used

### Mixed Content Support

Mixed content (text mixed with child elements) is handled intelligently:

- Text content is preserved in a `#text` field
- Use `--no-mixed-content` to ignore text in mixed elements

### Memory Efficiency

The converter uses streaming XML parsing to handle large files efficiently without loading the entire file into memory.

### Error Recovery

Comprehensive error handling for:
- Malformed XML
- File permission issues
- Unicode encoding problems
- Memory constraints
- Network path issues

## 💻 Programmatic Usage

You can also use the converter programmatically in your Python code:

```python
from xml2json import convert_xml_to_json, XMLToJSONConverter

# Simple conversion
success = convert_xml_to_json('input.xml', 'output.json')

# With options
success = convert_xml_to_json(
    'input.xml', 
    'output.json',
    preserve_root=False,
    strip_namespaces=True,
    pretty_print=False
)

# Using the class interface
converter = XMLToJSONConverter(
    preserve_root=False,
    strip_namespaces=True,
    empty_elements_as_null=True
)

success = converter.convert_file('input.xml', 'output.json')

# Batch conversion
success = converter.batch_convert('/path/to/xml', '/path/to/json')
```

### Available Functions

- `convert_xml_to_json()`: Convert single XML file
- `batch_convert_xml_to_json()`: Convert directory of XML files
- `XMLToJSONConverter`: Class-based interface with persistent options

## 🚨 Error Handling

The converter provides detailed error messages for common issues:

### File Not Found
```
ERROR: Input file 'missing.xml' does not exist.
```

### Invalid XML
```
ERROR: Error parsing XML file: not well-formed (invalid token): line 5, column 12
Tip: Check if XML file is well-formed and has proper encoding.
```

### Permission Issues
```
ERROR: Permission denied when accessing files.
Tip: Check file permissions and write access to output directory.
```

### Unicode Issues
```
ERROR: Unicode decode error: 'utf-8' codec can't decode byte 0xff
Tip: Check file encoding. Try specifying encoding explicitly.
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Run basic tests
python3 test_xml2json.py

# Run with pytest (if available)
python3 -m pytest test_xml2json.py -v

# Run specific test categories
python3 -m unittest test_xml2json.TestXMLToJSONCore -v
```

### Test Coverage

The test suite includes:
- ✅ Basic XML structures
- ✅ Complex nested elements
- ✅ Attributes and mixed content
- ✅ Namespace handling
- ✅ Error conditions
- ✅ Unicode content
- ✅ Large file handling
- ✅ Batch processing
- ✅ Edge cases

## 📊 Performance

### Benchmarks

Typical performance on modern hardware:

| File Size | Elements | Conversion Time | Memory Usage |
|-----------|----------|----------------|--------------|
| 1 MB | 1,000 | < 1 second | ~5 MB |
| 10 MB | 10,000 | ~2 seconds | ~15 MB |
| 100 MB | 100,000 | ~15 seconds | ~50 MB |

### Performance Tips

1. **Use `--compact` for large files** to reduce output size
2. **Use `--strip-namespaces`** if you don't need namespace information
3. **Process files in batches** rather than individually for better efficiency
4. **Use `--quiet` mode** for better performance when processing many files

## 🔍 Troubleshooting

### Common Issues

**Q: Getting "TypeError: 'type' object is not subscriptable"**

A: You're using Python < 3.9. The current version is compatible with Python 3.6+.

**Q: XML file appears to be empty or malformed**

A: Check the file encoding and ensure it's valid XML:
```bash
# Check file encoding
file -bi yourfile.xml

# Validate XML
xmllint --noout yourfile.xml  # if xmllint is available
```

**Q: Output JSON is very large**

A: Use `--compact` to reduce file size and `--strip-namespaces` if applicable.

**Q: Some text content is missing**

A: Check if you're using `--no-mixed-content`. Mixed content text is preserved by default.

### Debug Mode

Use verbose mode to see detailed processing information:

```bash
python3 xml2json.py input.xml --verbose
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python3 test_xml2json.py`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for new functions
- Include tests for new features

## ⚠ Disclaimer

**This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.**

### Important Notes:

- **Use at your own risk** - Always test with your data before using in production environments
- **Data backup recommended** - Make backups of important XML files before conversion
- **No warranty on output accuracy** - Verify converted JSON meets your requirements
- **User responsibility** - You are responsible for validating the tool's suitability for your use case

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. The MIT License includes additional warranty disclaimers and limitations of liability.

## 🙏 Acknowledgments

- Python ElementTree library for XML parsing
- The Python community for excellent documentation and examples
- Contributors who have helped improve this tool

## 🔗 Related Projects

- [xmltodict](https://github.com/martinblech/xmltodict) - Another XML to dict converter
- [json2xml](https://github.com/vinitkumar/json2xml) - Convert JSON back to XML
- [lxml](https://lxml.de/) - More powerful XML processing library

---

**Made with ❤️ for the Python community** | **Use responsibly and at your own risk**
