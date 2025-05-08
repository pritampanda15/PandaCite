# ===== Command-Line Interface =====
"""
Command-line interface for PandaCite
"""
import argparse
import sys
from .citation_manager import EnhancedCitationManager
import requests
import json
import sys
import os
import re
import argparse
from typing import Dict, Any, List, Optional, Tuple
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urlparse
from docx import Document
from colorama import Fore, Back, Style, init
from colorama import deinit
import sys
from colorama import init
init()
HAS_COLOR = True
import sys
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter

# Replace the has_colors import with this
HAS_COLOR = sys.stdout.isatty()  # Basic check if stdout is a terminal
# Initialize colorama
init(autoreset=True)
# Deinitialize colorama on exit
def cleanup():
    """Deinitialize colorama"""
    deinit()
import atexit
atexit.register(cleanup)
# Import citation formatters and parsers

from pandacite.formatters import (
    ElsevierFormatter,
    SpringerFormatter,
    APAFormatter,
    NatureFormatter,
    ScienceFormatter,
    IEEEFormatter,
    ChicagoFormatter,
    MLAFormatter,
    HarvardFormatter,
    VancouverFormatter,
    BMCFormatter,
    PLOSFormatter,
    CellFormatter,
    JAMAFormatter,
    BMJFormatter,
    NEJMFormatter,
    JBCFormatter,
    RSCFormatter,
    ACSFormatter,
    AIPFormatter,
    ACMFormatter,
    OxfordFormatter
)
from pandacite.parsers import (
    DOIParser,
    PMIDParser,
    ArXivParser,
    ISBNParser,
    URLParser,
    BibTexParser,
    RISParser
)
from pandacite.extractors.metadata import EnhancedMetadataExtractor
from pandacite.extractors.detector import IDDetector
from pandacite.processors.word import CommandLineWordProcessor
from pandacite.processors.numbered import NumberedCitationProcessor

# ASCII art for PandaCite banner
PANDA_BANNER = r"""
 _______                            __             ______   __    __               
/       \                          /  |           /      \ /  |  /  |              
$$$$$$$  | ______   _______    ____$$ |  ______  /$$$$$$  |$$/  _$$ |_     ______  
$$ |__$$ |/      \ /       \  /    $$ | /      \ $$ |  $$/ /  |/ $$   |   /      \ 
$$    $$/ $$$$$$  |$$$$$$$  |/$$$$$$$ | $$$$$$  |$$ |      $$ |$$$$$$/   /$$$$$$  |
$$$$$$$/  /    $$ |$$ |  $$ |$$ |  $$ | /    $$ |$$ |   __ $$ |  $$ | __ $$    $$ |
$$ |     /$$$$$$$ |$$ |  $$ |$$ \__$$ |/$$$$$$$ |$$ \__/  |$$ |  $$ |/  |$$$$$$$$/ 
$$ |     $$    $$ |$$ |  $$ |$$    $$ |$$    $$ |$$    $$/ $$ |  $$  $$/ $$       |
$$/       $$$$$$$/ $$/   $$/  $$$$$$$/  $$$$$$$/  $$$$$$/  $$/    $$$$/   $$$$$$$/ 
                                                                                   
"""

# Simple Unicode panda for smaller outputs
SMALL_PANDA = "ʕ •ᴥ• ʔ"

# Function to print the banner
def print_banner():
    """Print the PandaCite banner"""
    print(PANDA_BANNER)
    print("  Citation manager for researchers & writers")
    print()
# Function to print the small panda
def print_small_panda():
    """Print a small panda"""
    print(SMALL_PANDA)
    print("  Citation manager for researchers & writers")
    print()

# Add these panda constants to your CLI file for more options

# Cute mini panda - great for small notifications 
MINI_PANDA = "🐼"

# Detailed UTF-8 panda
DETAILED_PANDA = """
   ▄▀▀▀▄▄▄▄▄▄▄▀▀▀▄    
   █▒▒░░░░░░░░░▒▒█    
  █░░█░░░░░░█░░░░█    PandaCite
 ▄▄█░░░▀█▀░░░░░░█▄▄   
 █░░░░░░▀░░░░░░░░░█   Citation manager for 
 █░░░░░░░░▀▀░░░░░░█   researchers & writers
   █░░░░░░░░░░░░░█    
    █░░░▄▄▄▄▄░░█     
     █░░░░░░░░░█      
"""

# Panda progress indicator array (for loading animations)
PANDA_PROGRESS = [
    "  ʕ •ᴥ• ʔ   ",
    "  ʕ •ᴥ• ʔ.  ",
    "  ʕ •ᴥ• ʔ.. ",
    "  ʕ •ᴥ• ʔ...",
    "  ʕ •ᴥ• ʔ.. ",
    "  ʕ •ᴥ• ʔ.  "
]

# Panda faces showing different emotions
PANDA_FACES = {
    "normal": "ʕ •ᴥ• ʔ",
    "happy": "ʕ ᵔᴥᵔ ʔ",
    "sad": "ʕ ´•ᴥ•` ʔ",
    "excited": "ʕ •̀ω•́ ʔ",
    "working": "ʕ⁎̯͡⁎ʔ",
    "confused": "ʕ ಡ ﹏ ಡ ʔ",
    "sleepy": "ʕ￫ᴥ￩ʔ",
    "citation": "ʕ ﹁ ᴥ ﹁ ʔ〈",
    "error": "ʕノ•ᴥ•ʔノ ︵ ┻━┻",
    "done": "ʕっ•ᴥ•ʔっ 📝"
}

# Function to show a progress animation
def show_panda_progress(message, iterations=10, delay=0.2):
    """
    Show a cute panda progress animation
    
    Args:
        message: Message to display
        iterations: Number of animation cycles
        delay: Delay between frames in seconds
    """
    try:
        import time
        import sys
        
        for i in range(iterations):
            idx = i % len(PANDA_PROGRESS)
            # Clear line and print progress
            sys.stdout.write("\r" + message + " " + PANDA_PROGRESS[idx])
            sys.stdout.flush()
            time.sleep(delay)
        
        # Clear the animation when done
        sys.stdout.write("\r" + " " * (len(message) + 20) + "\r")
        sys.stdout.flush()
    except Exception:
        # On error, just print the message without animation
        print(message)

# Function to print a panda face with a message
def print_panda_message(message, mood="normal"):
    """
    Print a message with a panda face showing the specified mood
    
    Args:
        message: Message to display
        mood: Panda's mood from PANDA_FACES dictionary
    """
    face = PANDA_FACES.get(mood, PANDA_FACES["normal"])
    
    if HAS_COLOR:
        print(f"{Fore.BLACK}{Back.WHITE}{face}{Style.RESET_ALL} {Fore.CYAN}{message}{Style.RESET_ALL}")
    else:
        print(f"{face} {message}")

def main():
    """Main entry point for the citation manager"""
       
    parser = argparse.ArgumentParser(description="PandaCite: A Python-based Citation Manager")
    print_banner()
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Define available formats
    format_choices = [
        "elsevier", "springer", "apa", "nature", "science", "ieee", 
        "chicago", "mla", "harvard", "vancouver", "bmc", "plos", "cell",
        "jama", "bmj", "nejm", "jbc", "rsc", "acs", "aip", "acm", "oxford"
    ]
    
    # Define available ID types
    id_type_choices = ["doi", "pmid", "arxiv", "isbn", "url", "bibtex", "ris", "auto"]
    
    # Single citation parser
    single_parser = subparsers.add_parser("single", help="Generate a single citation")
    single_parser.add_argument("--id-type", "-t", choices=id_type_choices, default="auto", 
                              help="Type of identifier")
    single_parser.add_argument("--id", "-i", required=True, help="Identifier value")
    single_parser.add_argument("--format", "-f", choices=format_choices, 
                              default="apa", help="Citation format")
    single_parser.add_argument("--output", "-o", help="Output file path")
    single_parser.add_argument("--bibtex", "-b", help="Export as BibTeX to file")
    
    # Batch citation parser
    batch_parser = subparsers.add_parser("batch", help="Process multiple citations")
    batch_parser.add_argument("--id-type", "-t", choices=id_type_choices, default="auto", 
                             help="Type of identifier")
    batch_parser.add_argument("--ids", "-i", nargs="+", help="List of identifiers")
    batch_parser.add_argument("--file", "-l", help="File containing identifiers (one per line)")
    batch_parser.add_argument("--format", "-f", choices=format_choices, 
                             default="apa", help="Citation format")
    batch_parser.add_argument("--output", "-o", help="Output file path")
    batch_parser.add_argument("--bibtex", "-b", help="Export as BibTeX to file")
    
    # Word document parser
    word_parser = subparsers.add_parser("word", help="Process Word documents")
    word_parser.add_argument("--input", "-i", required=True, help="Input Word document")
    word_parser.add_argument("--output", "-o", required=True, help="Output Word document")
    word_parser.add_argument("--format", "-f", choices=format_choices, default="apa", 
                           help="Citation format")
    word_parser.add_argument("--id-list", "-l", help="File containing identifiers for the bibliography")
    word_parser.add_argument("--id-type", "-t", choices=id_type_choices, 
                           default="auto", help="Type of identifiers in the ID list")
    
    # Interactive mode parser
    interactive_parser = subparsers.add_parser("interactive", help="Run in interactive mode")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create citation manager
    citation_manager = EnhancedCitationManager()
    
    # If no arguments provided, show help with panda
    if len(sys.argv) == 1:
        parser.print_help()
        print(f"\n{SMALL_PANDA}  Use 'pandacite interactive' for the menu-driven interface")
        return
    
    if args.command == "single":
        # Process a single citation
        print_panda_message("Processing citation...", "working")
        citation = citation_manager.process_single_citation(
            args.id_type, args.id, args.format
        )
        
        if citation:
            print_panda_message("Citation generated successfully!", "happy")
            print("\nGenerated Citation:")
            print(citation)
            
            if args.output:
                if citation_manager.export_citations([citation], args.output):
                    print_panda_message("Citation generated successfully!", "happy")
                    print(f"\nCitation exported to {args.output}")
                else:
                    print_panda_message(f"Failed to export citation to {args.output}", "sad")
            
            if args.bibtex:
                if citation_manager.export_bibtex(args.bibtex):
                    print_panda_message(f"Failed to export citation to {args.output}", "sad")
                else:
                    print_panda_message(f"Failed to export citation to {args.output}", "sad")
        else:
            print_panda_message(f"Failed to generate citation for {args.id_type} {args.id}", "error")
    
    elif args.command == "batch":
        # Process multiple citations
        if args.file:
            citations = citation_manager.process_file(args.file, args.id_type, args.format)
        elif args.ids:
            citations = citation_manager.process_batch_citations(args.ids, args.id_type, args.format)
        else:
            print("Error: Either --ids or --file must be provided for batch processing")
            return
        
        if citations:
            print(f"\nGenerated {len(citations)} citations:")
            for i, citation in enumerate(citations, 1):
                print(f"\n{i}. {citation}")
            
            if args.output:
                if citation_manager.export_citations(citations, args.output):
                    print(f"\nCitations exported to {args.output}")
                else:
                    print(f"\nFailed to export citations to {args.output}")
            
            if args.bibtex:
                if citation_manager.export_bibtex(args.bibtex):
                    print(f"\nBibTeX exported to {args.bibtex}")
                else:
                    print(f"\nFailed to export BibTeX to {args.bibtex}")
        else:
            print("\nNo citations generated")
    
    elif args.command == "word":
        # Process Word document
        print_panda_message(f"Failed to generate citation for {args.id_type} {args.id}", "error")
        handle_word_command(args, citation_manager)
    
    elif args.command == "interactive":
        # Run in interactive mode
        run_interactive_mode(citation_manager, format_choices, id_type_choices)
    
    else:
        # Show help if no command is provided
        parser.print_help()
        print()
        print_panda_message("Use 'pandacite interactive' for the menu-driven interface", "citation")
    

# Add this to the handle_word_command function in complete_citation_manager.py

def handle_word_command(args, citation_manager):
    """Handle the word document processing command"""
    if not args.input or not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        return
    
    # Check if python-docx is installed
    try:
        import docx
    except ImportError:
        print("Error: python-docx package is required for Word document processing")
        print("Please install it with: pip install python-docx")
        return
    
    print(f"Processing Word document: {args.input}")
    print(f"Citation format: {args.format}")
    
    # Create ID detector
    id_detector = IDDetector()
    
    # Create Word processor
    word_processor = CommandLineWordProcessor(citation_manager)
    
    # Process the document
    document, citations = word_processor.process_document(args.input, args.format, id_detector)
    
    # Extract metadata for citations
    show_panda_progress("Extracting metadata from citations", 15, 0.1)
    extracted_metadata = {}
    citation_lookup = {}  # Map source_text to metadata keys
    
    # Load identifiers from file if provided
    identifiers = []
    if args.id_list and os.path.exists(args.id_list):
        with open(args.id_list, "r") as file:
            identifiers = [line.strip() for line in file if line.strip()]
        
        for identifier in identifiers:
            if args.id_type == "auto":
                id_type = id_detector.detect_id_type(identifier)
            else:
                id_type = args.id_type
            
            print(f"Processing identifier: {identifier} (type: {id_type})")
            metadata = citation_manager.extract_metadata(id_type, identifier)
            
            if metadata:
                key = f"{id_type}-{identifier}-metadata"
                extracted_metadata[key] = metadata
                
                # Create default source text for this citation
                if "authors" in metadata and metadata["authors"] and "year" in metadata:
                    first_author = metadata["authors"][0].split(",")[0]
                    year = metadata["year"]
                    if len(metadata["authors"]) > 1:
                        source_text = f"{first_author} et al., {year}"
                    else:
                        source_text = f"{first_author}, {year}"
                    citation_lookup[source_text.lower()] = key
                
                print(f"  Extracted metadata for {id_type} {identifier}")
                
    
    # Extract metadata from citations found in the document
    for citation_key, citation in citations.items():
        if "id_type" in citation and "id_value" in citation:
            id_type = citation["id_type"]
            id_value = citation["id_value"]
            
            print(f"Processing direct identifier in document: {id_type} {id_value}")
            metadata = citation_manager.extract_metadata(id_type, id_value)
            
            if metadata:
                key = f"{id_type}-{id_value}-metadata"
                extracted_metadata[key] = metadata
                citation_lookup[citation["source_text"].lower()] = key
                print(f"  Extracted metadata for {id_type} {id_value}")
    
    # Match author-year citations with metadata
    for citation_key, citation in citations.items():
        # Skip citations we've already processed
        if "source_text" in citation and citation["source_text"].lower() in citation_lookup:
            continue
            
        if "pattern" in citation and citation["pattern"] == "author_year":
            author = citation["author"].lower()
            year = citation["year"]
            source_text = citation["source_text"].lower()
            
            print(f"Processing author-year citation: {citation['source_text']}")
            
            # First check if we already have this exact source text
            if source_text in citation_lookup:
                continue
                
            # Try to find a matching metadata entry
            matched = False
            for metadata_key, metadata in extracted_metadata.items():
                if "authors" in metadata and metadata["authors"] and "year" in metadata:
                    # Get the first author's last name
                    first_author = metadata["authors"][0].split(",")[0].lower()
                    metadata_year = metadata["year"]
                    
                    # Check if this metadata matches our citation
                    if (first_author in author or author in first_author) and year == metadata_year:
                        citation_lookup[source_text] = metadata_key
                        print(f"  Matched citation {citation_key} with metadata {metadata_key}")
                        matched = True
                        break
            
            # If no match found, try to fetch metadata for this author/year
            if not matched:
                print(f"  No metadata match found for {citation['source_text']}, attempting to search...")
                try:
                    # Attempt to search for this publication
                    search_query = f"{citation['author']} {citation['year']}"
                    
                    # Try to make a naive DOI search via Crossref
                    search_url = f"https://api.crossref.org/works?query={search_query.replace(' ', '+')}&rows=1"
                    response = requests.get(search_url)
                    data = response.json()
                    
                    if "message" in data and "items" in data["message"] and data["message"]["items"]:
                        item = data["message"]["items"][0]
                        if "DOI" in item:
                            doi = item["DOI"]
                            print(f"  Found potential DOI: {doi}")
                            metadata = citation_manager.metadata_extractor.extract_from_doi(doi)
                            
                            if metadata:
                                key = f"doi-{doi}-metadata"
                                extracted_metadata[key] = metadata
                                citation_lookup[source_text] = key
                                print(f"  Successfully retrieved metadata for {citation['source_text']} via DOI search")
                            else:
                                print(f"  Failed to extract metadata from found DOI: {doi}")
                        else:
                            print("  Found search result but no DOI available")
                    else:
                        print("  No search results found")
                        
                    # Even if we didn't find metadata, create a placeholder
                    if source_text not in citation_lookup:
                        # Create minimal metadata from the citation itself
                        minimal_metadata = {
                            "title": f"[No title found for {citation['source_text']}]",
                            "authors": [f"{citation['author'].strip()}, "],
                            "year": citation["year"],
                            "journal": "[Journal not found]"
                        }
                        key = f"placeholder-{citation_key}"
                        extracted_metadata[key] = minimal_metadata
                        citation_lookup[source_text] = key
                        print(f"  Created placeholder metadata for {citation['source_text']}")
                        
                except Exception as e:
                    print(f"  Error searching for metadata: {e}")
                    # Create minimal metadata as a fallback
                    minimal_metadata = {
                        "title": f"[No title found for {citation['source_text']}]",
                        "authors": [f"{citation['author'].strip()}, "],
                        "year": citation["year"],
                        "journal": "[Journal not found]"
                    }
                    key = f"placeholder-{citation_key}"
                    extracted_metadata[key] = minimal_metadata
                    citation_lookup[source_text] = key
                    print(f"  Created placeholder metadata for {citation['source_text']}")
    
    # Link citations to their metadata using the lookup table
    for citation_key, citation in citations.items():
        if "source_text" in citation:
            source_text = citation["source_text"].lower()
            if source_text in citation_lookup:
                metadata_key = citation_lookup[source_text]
                citation["metadata_key"] = metadata_key
                print(f"Linked citation '{citation['source_text']}' to metadata key '{metadata_key}'")
    
    # Update the document with citations
    if extracted_metadata:
        # Print a summary of what will be updated
        print_panda_message(f"Found {len(extracted_metadata)} references to format", "happy")
        for i, (key, metadata) in enumerate(extracted_metadata.items(), 1):
            formatter = citation_manager.formatters.get(args.format.lower())
            if formatter:
                citation_str = formatter.format_citation(metadata)
                author_str = ""
                if metadata.get("authors"):
                    if len(metadata["authors"]) == 1:
                        author_str = metadata["authors"][0].split(",")[0]
                    else:
                        author_str = metadata["authors"][0].split(",")[0] + " et al."
                year_str = metadata.get("year", "")
                print(f"{i}. {author_str} ({year_str}) - Will be formatted as full citation")
            
    #     # Proceed with document update
    #     word_processor.update_document_with_citations(
    #         document, citations, extracted_metadata, args.format, args.output
    #     )
    # else:
    #     print("No metadata extracted. Cannot update the document.")
        if args.format.lower() in ["vancouver", "ieee"]:
            print("Using numbered citation style...")
            numbered_processor = NumberedCitationProcessor(citation_manager)
            citation_numbers = numbered_processor.process_document(document, citations, extracted_metadata, args.format)
            
            # Replace in-text citations with numbers
            numbered_processor.format_in_text_citations(document, citations, citation_numbers)
            
            # Generate numbered bibliography
            numbered_processor.generate_numbered_bibliography(document, extracted_metadata, citation_numbers, args.format)
            
            # Save document
            try:
                document.save(args.output)
                print(f"Document saved to {args.output} with numbered citations")
                return
            except Exception as e:
                print(f"Error saving document with numbered citations: {e}")
                print_panda_message(f"Document saved to {args.output}", "done")
                # Continue to standard processing as fallback
        else:
            # Standard processing for non-numbered styles
            word_processor.update_document_with_citations(
                document, citations, extracted_metadata, args.format, args.output
            )
    else:
        print_panda_message("No metadata extracted. Cannot update the document.", "sad")



def get_file_path(prompt_text):
    completer = PathCompleter(only_files=True)
    return prompt(prompt_text, completer=completer)

def run_interactive_mode(citation_manager, format_choices, id_type_choices):
    """Run the citation manager in interactive mode"""
    print("\nEnhanced Citation Manager - Interactive Mode")
    print("===========================================")
    
    while True:
        print("\nOptions:")
        print("1. Generate a single citation")
        print("2. Process multiple citations")
        print("3. Process citations from a file")
        print("4. Process a Word document")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            # Single citation
            id_type = get_valid_input(
                f"Enter ID type ({'/'.join(id_type_choices)}): ", 
                lambda x: x.lower() in id_type_choices,
                "auto"
            )
            
            id_value = input("Enter ID value: ")
            
            format_name = get_valid_input(
                f"Enter citation format ({'/'.join(format_choices)}): ", 
                lambda x: x.lower() in format_choices,
                "apa"
            )
            
            print("\nProcessing citation...")
            citation = citation_manager.process_single_citation(id_type, id_value, format_name)
            
            if citation:
                print("\nGenerated Citation:")
                print(citation)
                
                save_option = input("\nSave to file? (y/n): ")
                if save_option.lower() == "y":
                    output_path = input("Enter output file path: ")
                    citation_manager.export_citations([citation], output_path)
                    print(f"Citation saved to {output_path}")
                
                bibtex_option = input("\nExport as BibTeX? (y/n): ")
                if bibtex_option.lower() == "y":
                    bibtex_path = input("Enter BibTeX file path: ")
                    citation_manager.export_bibtex(bibtex_path)
                    print(f"BibTeX exported to {bibtex_path}")
            else:
                print(f"\nFailed to generate citation for {id_type} {id_value}")
        
        elif choice == "2":
            # Batch citations
            id_type = get_valid_input(
                f"Enter ID type ({'/'.join(id_type_choices)}): ", 
                lambda x: x.lower() in id_type_choices,
                "auto"
            )
            
            print("Enter IDs (one per line, empty line to finish):")
            ids = []
            while True:
                id_line = input()
                if not id_line:
                    break
                ids.append(id_line)
            
            if not ids:
                print("No IDs entered")
                continue
            
            format_name = get_valid_input(
                f"Enter citation format ({'/'.join(format_choices)}): ", 
                lambda x: x.lower() in format_choices,
                "apa"
            )
            
            print("\nProcessing citations...")
            citations = citation_manager.process_batch_citations(ids, id_type, format_name)
            
            if citations:
                print(f"\nGenerated {len(citations)} citations:")
                for i, citation in enumerate(citations, 1):
                    print(f"\n{i}. {citation}")
                
                save_option = input("\nSave to file? (y/n): ")
                if save_option.lower() == "y":
                    output_path = input("Enter output file path: ")
                    citation_manager.export_citations(citations, output_path)
                    print(f"Citations saved to {output_path}")
                
                bibtex_option = input("\nExport as BibTeX? (y/n): ")
                if bibtex_option.lower() == "y":
                    bibtex_path = input("Enter BibTeX file path: ")
                    citation_manager.export_bibtex(bibtex_path)
                    print(f"BibTeX exported to {bibtex_path}")
            else:
                print("\nNo citations generated")
        
        elif choice == "3":
            # Process from file
            id_type = get_valid_input(
                f"Enter ID type ({'/'.join(id_type_choices)}): ", 
                lambda x: x.lower() in id_type_choices,
                "auto"
            )
            
            file_path = input("Enter file path: ")
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
            
            format_name = get_valid_input(
                f"Enter citation format ({'/'.join(format_choices)}): ", 
                lambda x: x.lower() in format_choices,
                "apa"
            )
            
            print("\nProcessing citations from file...")
            citations = citation_manager.process_file(file_path, id_type, format_name)
            
            if citations:
                print(f"\nGenerated {len(citations)} citations:")
                for i, citation in enumerate(citations, 1):
                    print(f"\n{i}. {citation}")
                
                save_option = input("\nSave to file? (y/n): ")
                if save_option.lower() == "y":
                    output_path = input("Enter output file path: ")
                    citation_manager.export_citations(citations, output_path)
                    print(f"Citations saved to {output_path}")
                
                bibtex_option = input("\nExport as BibTeX? (y/n): ")
                if bibtex_option.lower() == "y":
                    bibtex_path = input("Enter BibTeX file path: ")
                    citation_manager.export_bibtex(bibtex_path)
                    print(f"BibTeX exported to {bibtex_path}")
            else:
                print("\nNo citations generated")
        
        elif choice == "4":
            # Process Word document
            try:
                from docx import Document
            except ImportError:
                print("Error: python-docx package is required for Word document processing")
                print("Please install it with: pip install python-docx")
                continue
            
            input_path = input("Enter input Word document path: ")
            if not os.path.exists(input_path):
                print(f"File not found: {input_path}")
                continue
            
            output_path = input("Enter output Word document path: ")
            
            format_name = get_valid_input(
                f"Enter citation format ({'/'.join(format_choices)}): ", 
                lambda x: x.lower() in format_choices,
                "apa"
            )
            
            id_list_option = input("Do you have a file with identifiers for the bibliography? (y/n): ")
            id_list_path = None
            id_type = "auto"
            
            if id_list_option.lower() == "y":
                id_list_path = input("Enter identifier list file path: ")
                if not os.path.exists(id_list_path):
                    print(f"File not found: {id_list_path}")
                    continue
                
                id_type = get_valid_input(
                    f"Enter ID type ({'/'.join(id_type_choices)}): ", 
                    lambda x: x.lower() in id_type_choices,
                    "auto"
                )
            
            print("\nProcessing Word document...")
            
            # Create args object for the handle_word_command function
            class Args:
                pass
            
            args = Args()
            args.input = input_path
            args.output = output_path
            args.format = format_name
            args.id_list = id_list_path
            args.id_type = id_type
            
            handle_word_command(args, citation_manager)
        
        elif choice == "5":
            # Exit
            print("\nExiting Citation Manager. Goodbye!")
            break
        
        else:
            print("\nInvalid choice. Please enter a number between 1 and 5.")

def get_valid_input(prompt, validator, default=None):
    """
    Get valid input from the user
    
    Args:
        prompt: Prompt to display
        validator: Function to validate input
        default: Default value if input is empty
    
    Returns:
        Valid input
    """
    while True:
        user_input = input(prompt)
        
        if not user_input and default:
            return default
        
        if validator(user_input):
            return user_input.lower()
        
        print("Invalid input. Please try again.")

if __name__ == "__main__":
    main()
