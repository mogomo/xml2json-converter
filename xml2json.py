#!/usr/bin/env python3
"""
XML to JSON Converter
Converts XML files to JSON format with proper handling of various XML structures,
namespaces, and mixed content.
"""

import json
import sys
import os
import xml.etree.ElementTree as ET
from typing import Union, Optional, Dict, Any, List
import argparse
import logging
import textwrap
from pathlib import Path

# Type aliases for better clarity (compatible with older Python versions)
JsonValue = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
XmlDict = Dict[str, JsonValue]


def xml_to_dict(element: ET.Element, 
                strip_namespaces: bool = False,
                preserve_mixed_content: bool = True,
                empty_elements_as_null: bool = False) -> JsonValue:
    """
    Convert XML element to dictionary recursively.
    
    Args:
        element: XML element to convert
        strip_namespaces: Remove XML namespaces from element names
        preserve_mixed_content: Handle mixed content (text + children)
        empty_elements_as_null: Represent empty elements as null vs empty dict
        
    Returns:
        Dictionary, string, or None representation of XML element
    """
    result: XmlDict = {}
    
    # Strip namespace if requested
    def clean_tag(tag: str) -> str:
        if strip_namespaces and '}' in tag:
            return tag.split('}', 1)[1]
        return tag
    
    # Add attributes with @ prefix
    if element.attrib:
        for key, value in element.attrib.items():
            clean_key = clean_tag(key)
            result[f'@{clean_key}'] = value
    
    # Handle text content
    text_content = ""
    if element.text:
        text_content = element.text.strip()
    
    # Handle child elements
    children: Dict[str, JsonValue] = {}
    for child in element:
        child_tag = clean_tag(child.tag)
        child_data = xml_to_dict(child, strip_namespaces, preserve_mixed_content, empty_elements_as_null)
        
        if child_tag in children:
            # Convert to list if multiple elements with same tag
            if not isinstance(children[child_tag], list):
                children[child_tag] = [children[child_tag]]
            children[child_tag].append(child_data)
        else:
            children[child_tag] = child_data
    
    # Combine results based on content type and options
    if children:
        result.update(children)
        if text_content and preserve_mixed_content:
            result['#text'] = text_content
    elif text_content:
        if result:  # Has attributes
            result['#text'] = text_content
        else:  # No attributes, return text directly
            return text_content
    elif not result:
        # Empty element handling
        return None if empty_elements_as_null else {}
    
    return result if result else (None if empty_elements_as_null else {})


def preprocess_xml_tree(tree: ET.ElementTree, strip_namespaces: bool = False) -> None:
    """
    Preprocess XML tree to handle namespaces if needed.
    
    Args:
        tree: XML tree to preprocess
        strip_namespaces: Whether to strip namespaces
    """
    if strip_namespaces:
        for elem in tree.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]
            # Also strip namespaces from attribute names
            if elem.attrib:
                new_attrib = {}
                for key, value in elem.attrib.items():
                    new_key = key.split('}', 1)[1] if '}' in key else key
                    new_attrib[new_key] = value
                elem.attrib.clear()
                elem.attrib.update(new_attrib)


def convert_xml_to_json(input_file: Union[str, Path], 
                       output_file: Optional[Union[str, Path]] = None,
                       preserve_root: bool = True,
                       pretty_print: bool = True,
                       strip_namespaces: bool = False,
                       preserve_mixed_content: bool = True,
                       empty_elements_as_null: bool = False) -> bool:
    """
    Convert XML file to JSON format.
    
    Args:
        input_file: Path to input XML file
        output_file: Path to output JSON file (None for auto-generate, "-" for stdout)
        preserve_root: Keep root element as top-level key
        pretty_print: Format JSON with indentation
        strip_namespaces: Remove XML namespaces from element names
        preserve_mixed_content: Handle mixed content (text + children)
        empty_elements_as_null: Represent empty elements as null vs empty dict
        
    Returns:
        bool: True if conversion successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    input_path = Path(input_file)
    
    # Validate input file
    if not input_path.exists():
        logger.error(f"Input file '{input_path}' does not exist.")
        return False
    
    if not input_path.is_file():
        logger.error(f"'{input_path}' is not a regular file.")
        return False
    
    if not str(input_path).lower().endswith('.xml'):
        logger.warning(f"Input file '{input_path}' doesn't have .xml extension.")
    
    # Handle output file
    if output_file is None:
        # Auto-generate output filename
        output_path = input_path.with_suffix('.json')
    elif str(output_file) == '-':
        # Output to stdout
        output_path = None
    else:
        output_path = Path(output_file)
    
    # Ensure output directory exists (if not stdout)
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Parse XML
        logger.info(f"Parsing XML file: {input_path}")
        tree = ET.parse(input_path)
        
        # Preprocess tree if needed
        preprocess_xml_tree(tree, strip_namespaces)
        
        root = tree.getroot()
        
        # Convert to dictionary
        if preserve_root:
            json_data = {root.tag: xml_to_dict(root, strip_namespaces, preserve_mixed_content, empty_elements_as_null)}
        else:
            json_data = xml_to_dict(root, strip_namespaces, preserve_mixed_content, empty_elements_as_null)
        
        # Prepare JSON output options
        json_options = {
            'ensure_ascii': False,
            'separators': (',', ': ') if pretty_print else (',', ':')
        }
        
        if pretty_print:
            json_options['indent'] = 2
        
        # Write JSON
        if output_path is None:
            # Output to stdout
            json.dump(json_data, sys.stdout, **json_options)
            sys.stdout.write('\n')  # Add newline for better CLI experience
            logger.info("JSON output written to stdout")
        else:
            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, **json_options)
            
            logger.info(f"Successfully converted '{input_path}' to '{output_path}'")
            
            # Display file size information
            input_size = input_path.stat().st_size
            output_size = output_path.stat().st_size
            logger.info(f"Input size: {input_size:,} bytes, Output size: {output_size:,} bytes")
        
        return True
        
    except ET.ParseError as e:
        logger.error(f"Error parsing XML file: {e}")
        logger.error("Tip: Check if XML file is well-formed and has proper encoding.")
        return False
    except FileNotFoundError:
        logger.error(f"Could not read file '{input_path}'.")
        return False
    except PermissionError:
        logger.error("Permission denied when accessing files.")
        logger.error("Tip: Check file permissions and write access to output directory.")
        return False
    except UnicodeDecodeError as e:
        logger.error(f"Unicode decode error: {e}")
        logger.error("Tip: Check file encoding. Try specifying encoding explicitly.")
        return False
    except MemoryError:
        logger.error("Out of memory. File may be too large to process.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def batch_convert_xml_to_json(input_dir: Union[str, Path], 
                             output_dir: Optional[Union[str, Path]] = None,
                             preserve_root: bool = True,
                             pretty_print: bool = True,
                             strip_namespaces: bool = False,
                             preserve_mixed_content: bool = True,
                             empty_elements_as_null: bool = False) -> bool:
    """
    Convert all XML files in a directory to JSON format.
    
    Args:
        input_dir: Directory containing XML files
        output_dir: Output directory for JSON files
        preserve_root: Keep root element as top-level key
        pretty_print: Format JSON with indentation
        strip_namespaces: Remove XML namespaces from element names
        preserve_mixed_content: Handle mixed content (text + children)
        empty_elements_as_null: Represent empty elements as null vs empty dict
        
    Returns:
        bool: True if all conversions successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    input_path = Path(input_dir)
    
    if not input_path.exists():
        logger.error(f"Input directory '{input_path}' does not exist.")
        return False
    
    if not input_path.is_dir():
        logger.error(f"'{input_path}' is not a directory.")
        return False
    
    # Set default output directory
    output_path = Path(output_dir) if output_dir else input_path
    
    # Find all XML files
    xml_files = [f for f in input_path.iterdir() 
                 if f.suffix.lower() == '.xml' and f.is_file()]
    
    if not xml_files:
        logger.error(f"No XML files found in directory '{input_path}'.")
        return False
    
    logger.info(f"Found {len(xml_files)} XML file(s) to convert.")
    
    success_count = 0
    for xml_file in xml_files:
        output_file = output_path / (xml_file.stem + '.json')
        
        logger.info(f"Converting: {xml_file.name}")
        if convert_xml_to_json(xml_file, output_file, preserve_root, pretty_print, 
                              strip_namespaces, preserve_mixed_content, empty_elements_as_null):
            success_count += 1
    
    logger.info(f"Batch conversion completed: {success_count}/{len(xml_files)} files converted successfully.")
    return success_count == len(xml_files)


class XMLToJSONConverter:
    """
    XML to JSON converter with configurable options.
    
    This class provides a convenient wrapper around the core conversion functions
    with persistent configuration options.
    """
    
    def __init__(self, 
                 preserve_root: bool = True,
                 pretty_print: bool = True,
                 strip_namespaces: bool = False,
                 preserve_mixed_content: bool = True,
                 empty_elements_as_null: bool = False):
        """
        Initialize converter with options.
        
        Args:
            preserve_root: Keep root element as top-level key
            pretty_print: Format JSON with indentation
            strip_namespaces: Remove XML namespaces from element names
            preserve_mixed_content: Handle mixed content (text + children)
            empty_elements_as_null: Represent empty elements as null vs empty dict
        """
        self.preserve_root = preserve_root
        self.pretty_print = pretty_print
        self.strip_namespaces = strip_namespaces
        self.preserve_mixed_content = preserve_mixed_content
        self.empty_elements_as_null = empty_elements_as_null
    
    def convert_file(self, input_file: Union[str, Path], 
                    output_file: Optional[Union[str, Path]] = None) -> bool:
        """
        Convert XML file to JSON format using instance settings.
        
        Args:
            input_file: Path to input XML file
            output_file: Path to output JSON file (None for auto-generate, "-" for stdout)
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        return convert_xml_to_json(
            input_file, output_file, self.preserve_root, self.pretty_print,
            self.strip_namespaces, self.preserve_mixed_content, self.empty_elements_as_null
        )
    
    def batch_convert(self, input_dir: Union[str, Path], 
                     output_dir: Optional[Union[str, Path]] = None) -> bool:
        """
        Convert all XML files in a directory to JSON format using instance settings.
        
        Args:
            input_dir: Directory containing XML files
            output_dir: Output directory for JSON files
            
        Returns:
            bool: True if all conversions successful, False otherwise
        """
        return batch_convert_xml_to_json(
            input_dir, output_dir, self.preserve_root, self.pretty_print,
            self.strip_namespaces, self.preserve_mixed_content, self.empty_elements_as_null
        )


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Setup logging configuration."""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert XML files to JSON format with advanced options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              %(prog)s input.xml                           Convert single file
              %(prog)s input.xml output.json               Convert with custom output name
              %(prog)s input.xml -                         Output to stdout
              %(prog)s -d /path/to/xml/files               Batch convert directory
              %(prog)s input.xml --no-root                 Convert without preserving root element
              %(prog)s input.xml --compact                 Generate compact JSON
              %(prog)s input.xml --strip-namespaces        Remove XML namespaces
              %(prog)s input.xml --no-mixed-content        Ignore mixed content text
              %(prog)s -d /path/xml --output-dir /path/json  Batch with custom output directory
            """)
    )
    
    parser.add_argument('input', nargs='?', 
                       help='Input XML file or directory (with -d flag)')
    parser.add_argument('output', nargs='?', 
                       help='Output JSON file (use "-" for stdout, ignored with -d flag)')
    
    # Mode options
    parser.add_argument('-d', '--directory', action='store_true',
                       help='Batch convert all XML files in input directory')
    parser.add_argument('--output-dir', 
                       help='Output directory for batch conversion')
    
    # Conversion options
    parser.add_argument('--no-root', action='store_true',
                       help='Do not preserve root element as top-level key')
    parser.add_argument('--compact', action='store_true',
                       help='Generate compact JSON without indentation')
    parser.add_argument('--strip-namespaces', action='store_true',
                       help='Remove XML namespaces from element and attribute names')
    parser.add_argument('--no-mixed-content', action='store_true',
                       help='Do not preserve mixed content (text within elements that have children)')
    parser.add_argument('--empty-as-null', action='store_true',
                       help='Represent empty XML elements as null instead of empty objects')
    
    # Logging options
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Suppress all output except errors')
    
    parser.add_argument('--version', action='version', version='%(prog)s 2.1')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose, args.quiet)
    logger = logging.getLogger(__name__)
    
    # Validate arguments
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.directory:
            success = batch_convert_xml_to_json(
                args.input, args.output_dir,
                preserve_root=not args.no_root,
                pretty_print=not args.compact,
                strip_namespaces=args.strip_namespaces,
                preserve_mixed_content=not args.no_mixed_content,
                empty_elements_as_null=args.empty_as_null
            )
        else:
            success = convert_xml_to_json(
                args.input, args.output,
                preserve_root=not args.no_root,
                pretty_print=not args.compact,
                strip_namespaces=args.strip_namespaces,
                preserve_mixed_content=not args.no_mixed_content,
                empty_elements_as_null=args.empty_as_null
            )
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    
