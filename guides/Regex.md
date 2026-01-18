# Regular Expressions (Regex) - Complete Guide

Regular expressions are powerful patterns used for matching, searching, and manipulating text. They're supported across virtually all programming languages and text editors.

---

## Core Concepts

### What is Regex?

A **regular expression** (regex or regexp) is a sequence of characters that defines a search pattern. It's used for:
- **Pattern matching**: Find specific text patterns
- **Validation**: Check if input matches required format
- **Extraction**: Pull specific data from text
- **Replacement**: Find and replace text
- **Splitting**: Break text into parts

---

### Basic Syntax

```regex
/pattern/flags
```

**Example:**
```regex
/hello/i          # Match "hello" case-insensitive
/\d{3}-\d{4}/     # Match phone format: 123-4567
/^[a-z]+@.+\..+$/ # Match basic email
```

---

## Literal Characters

### Simple Matching

```regex
cat               # Matches "cat" exactly
hello world       # Matches "hello world"
123               # Matches "123"
```

**Examples:**
- `cat` matches: "**cat**", "s**cat**ter", "lo**cat**ion"
- `hello` matches: "**hello** world", "say **hello**"

---

### Special Characters (Metacharacters)

Characters with special meaning that must be escaped with `\`:

```
. ^ $ * + ? { } [ ] \ | ( )
```

**Escaping:**
```regex
\.                # Literal dot
\*                # Literal asterisk
\(                # Literal opening parenthesis
\[                # Literal opening bracket
\\                # Literal backslash
```

**Examples:**
```regex
\$100             # Matches "$100"
file\.txt         # Matches "file.txt" (not "fileXtxt")
\(test\)          # Matches "(test)"
```

---

## Character Classes

### Predefined Character Classes

```regex
.                 # Any character except newline
\d                # Digit [0-9]
\D                # Non-digit [^0-9]
\w                # Word character [a-zA-Z0-9_]
\W                # Non-word character [^a-zA-Z0-9_]
\s                # Whitespace [ \t\n\r\f\v]
\S                # Non-whitespace [^ \t\n\r\f\v]
```

**Examples:**
```regex
\d\d\d            # Matches three digits: "123", "456"
\w+               # Matches one or more word chars: "hello", "test_123"
\s+               # Matches whitespace: " ", "  ", "\t\n"
```

---

### Custom Character Classes

```regex
[abc]             # Match a, b, or c
[a-z]             # Match any lowercase letter
[A-Z]             # Match any uppercase letter
[0-9]             # Match any digit
[a-zA-Z]          # Match any letter
[a-zA-Z0-9]       # Match any alphanumeric
[^abc]            # Match anything EXCEPT a, b, or c (negation)
```

**Examples:**
```regex
[aeiou]           # Matches any vowel: "a", "e", "i", "o", "u"
[^aeiou]          # Matches any consonant or non-letter
[0-9a-f]          # Matches hexadecimal digits
[A-Z][a-z]+       # Matches capitalized words: "Hello", "World"
```

---

### Character Class Ranges

```regex
[a-z]             # Lowercase letters
[A-Z]             # Uppercase letters
[0-9]             # Digits
[a-zA-Z]          # All letters
[a-zA-Z0-9]       # Alphanumeric
[a-z0-9._-]       # Letters, digits, and specific symbols
```

**Examples:**
```regex
[1-5]             # Matches: "1", "2", "3", "4", "5"
[a-fA-F0-9]       # Hex digits (case insensitive)
[!-/]             # ASCII range from ! to /
```

---

## Quantifiers

### Basic Quantifiers

```regex
*                 # 0 or more times
+                 # 1 or more times
?                 # 0 or 1 time (optional)
{n}               # Exactly n times
{n,}              # n or more times
{n,m}             # Between n and m times
```

**Examples:**
```regex
a*                # "", "a", "aa", "aaa"
a+                # "a", "aa", "aaa" (NOT "")
a?                # "", "a"
a{3}              # "aaa" (exactly 3)
a{2,4}            # "aa", "aaa", "aaaa"
a{2,}             # "aa", "aaa", "aaaa", "aaaaa", ...

\d+               # One or more digits: "1", "123", "9999"
\w{3,10}          # 3 to 10 word characters
[a-z]*            # Zero or more lowercase letters
```

---

### Greedy vs Lazy (Non-Greedy)

**Greedy (default):** Matches as much as possible
```regex
.*                # Greedy: matches everything
.+                # Greedy: matches one or more of anything
\d+               # Greedy: matches all consecutive digits
```

**Lazy:** Matches as little as possible (add `?` after quantifier)
```regex
.*?               # Lazy: matches as few chars as possible
.+?               # Lazy: matches minimum needed
\d+?              # Lazy: matches minimum digits needed
```

**Example:**
```
Text: <div>Hello</div><div>World</div>

/<div>.*<\/div>/   # Greedy: matches "<div>Hello</div><div>World</div>"
/<div>.*?<\/div>/  # Lazy: matches "<div>Hello</div>" (first occurrence)
```

**Lazy quantifiers:**
```regex
*?                # 0 or more (lazy)
+?                # 1 or more (lazy)
??                # 0 or 1 (lazy)
{n,m}?            # Between n and m (lazy)
{n,}?             # n or more (lazy)
```

---

## Anchors

### Position Anchors

```regex
^                 # Start of string/line
$                 # End of string/line
\b                # Word boundary
\B                # Non-word boundary
\A                # Start of string (multiline mode independent)
\Z                # End of string (multiline mode independent)
```

**Examples:**
```regex
^hello            # Matches "hello" only at start: "hello world"
world$            # Matches "world" only at end: "hello world"
^hello$           # Matches exactly "hello" (nothing before or after)
^\d+$             # Entire string must be digits
```

---

### Word Boundaries

```regex
\b                # Word boundary
\B                # Non-word boundary
```

**Examples:**
```regex
\bcat\b           # Matches "cat" as whole word
                  # Matches: "a cat runs"
                  # NOT: "scatter", "category"

\Bcat\B           # Matches "cat" NOT at word boundary
                  # Matches: "s**cat**ter", "lo**cat**ion"
                  # NOT: "cat", "a cat"

\btest            # Matches "test" at word start: "test", "testing"
test\b            # Matches "test" at word end: "test", "retest"
```

---

## Groups and Capturing

### Capturing Groups

```regex
(pattern)         # Capture group
(a|b)             # Alternation: a OR b
```

**Examples:**
```regex
(hello)           # Captures "hello"
(\d{3})           # Captures 3 digits
(cat|dog)         # Matches and captures "cat" OR "dog"
(Mr|Mrs|Ms)\.     # Matches "Mr.", "Mrs.", or "Ms."

# Phone number with groups
(\d{3})-(\d{3})-(\d{4})
# Captures: "123" "456" "7890" from "123-456-7890"
```

---

### Non-Capturing Groups

```regex
(?:pattern)       # Non-capturing group (for grouping only)
```

**Examples:**
```regex
(?:cat|dog)s?     # Match "cat", "cats", "dog", "dogs"
                  # No capture, just grouping

(?:https?://)     # Match "http://" or "https://"
                  # No capture needed

# Capturing vs non-capturing
(cat|dog)         # Captures "cat" or "dog"
(?:cat|dog)       # Matches but doesn't capture
```

---

### Named Groups

```regex
(?<name>pattern)  # Named capture group (Python, .NET, PCRE)
(?P<name>pattern) # Named capture group (Python)
```

**Examples:**
```regex
(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})
# Matches "2024-01-15"
# Captures: year="2024", month="01", day="15"

(?<area>\d{3})-(?<exchange>\d{3})-(?<number>\d{4})
# Matches "555-123-4567"
# Captures: area="555", exchange="123", number="4567"

# Python syntax
(?P<username>\w+)@(?P<domain>[\w.]+)
# Matches "john@example.com"
# Captures: username="john", domain="example.com"
```

---

### Backreferences

Reference previously captured groups:

```regex
\1, \2, \3, ...   # Backreference to group 1, 2, 3, etc.
\k<name>          # Backreference to named group
```

**Examples:**
```regex
(\w+)\s+\1        # Matches repeated words
                  # Matches: "hello hello", "test test"
                  # NOT: "hello world"

(['"]).*?\1       # Match quoted string with same quote
                  # Matches: "hello" or 'world'
                  # Uses same quote to close

<(\w+)>.*?</\1>   # Match HTML tags
                  # Matches: <div>text</div>, <span>text</span>
                  # NOT: <div>text</span>

(\d{2})-\1        # Matches repeated number pair
                  # Matches: "12-12", "99-99"
```

---

## Alternation

```regex
|                 # OR operator
```

**Examples:**
```regex
cat|dog           # Matches "cat" OR "dog"
red|green|blue    # Matches "red", "green", or "blue"
Mr\.|Mrs\.|Ms\.   # Matches "Mr.", "Mrs.", or "Ms."

# With grouping
(jpg|png|gif)     # Match image extensions
https?            # Match "http" or "https" (? makes 's' optional)
colou?r           # Match "color" or "colour"
```

**Priority:**
```regex
cat|dog food      # Matches "cat" OR "dog food"
(cat|dog) food    # Matches "cat food" OR "dog food"
```

---

## Lookahead and Lookbehind

### Positive Lookahead

```regex
(?=pattern)       # Positive lookahead: followed by pattern
```

**Examples:**
```regex
\d+(?= dollars)   # Match digits followed by " dollars"
                  # "100 dollars" → matches "100"
                  # "100 euros" → no match

\w+(?=@)          # Match username before @
                  # "john@example.com" → matches "john"

hello(?= world)   # Matches "hello" only if followed by " world"
```

---

### Negative Lookahead

```regex
(?!pattern)       # Negative lookahead: NOT followed by pattern
```

**Examples:**
```regex
\d+(?! dollars)   # Match digits NOT followed by " dollars"
                  # "100 euros" → matches "100"
                  # "100 dollars" → no match

hello(?! world)   # Matches "hello" NOT followed by " world"
                  # "hello there" → matches
                  # "hello world" → no match
```

---

### Positive Lookbehind

```regex
(?<=pattern)      # Positive lookbehind: preceded by pattern
```

**Examples:**
```regex
(?<=\$)\d+        # Match digits after $
                  # "$100" → matches "100"
                  # "100" → no match

(?<=@)\w+         # Match domain after @
                  # "john@example" → matches "example"

(?<=Mr\. )\w+     # Match name after "Mr. "
                  # "Mr. Smith" → matches "Smith"
```

---

### Negative Lookbehind

```regex
(?<!pattern)      # Negative lookbehind: NOT preceded by pattern
```

**Examples:**
```regex
(?<!\$)\d+        # Match digits NOT after $
                  # "100" → matches "100"
                  # "$100" → no match

(?<!@)\w+         # Match word NOT after @
                  # "hello@world" → matches "hello"
```

---

### Lookaround Combinations

```regex
# Password validation: 8+ chars with at least one digit
(?=.*\d).{8,}

# Password: at least one uppercase and one lowercase
(?=.*[a-z])(?=.*[A-Z]).+

# Password: uppercase, lowercase, digit, 8+ chars
(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}

# Match word not preceded or followed by letter
(?<![a-zA-Z])\w+(?![a-zA-Z])
```

---

## Flags (Modifiers)

### Common Flags

```regex
/pattern/flags
```

| Flag | Name | Description |
|------|------|-------------|
| `i` | Case-insensitive | Match regardless of case |
| `g` | Global | Find all matches (not just first) |
| `m` | Multiline | `^` and `$` match line boundaries |
| `s` | Dotall/Single-line | `.` matches newlines |
| `u` | Unicode | Enable Unicode support |
| `x` | Extended/Verbose | Allow whitespace and comments |

---

### Flag Examples

**Case-insensitive (`i`):**
```regex
/hello/i          # Matches: "hello", "Hello", "HELLO"
/[a-z]+/i         # Matches any letters regardless of case
```

**Global (`g`):**
```regex
/cat/g            # Find all "cat" occurrences
                  # Without g: finds only first match
```

**Multiline (`m`):**
```regex
/^test/m          # Match "test" at start of any line
                  # Without m: only at start of string

/end$/m           # Match "end" at end of any line
                  # Without m: only at end of string
```

**Dotall (`s`):**
```regex
/.+/s             # Matches across newlines
                  # "hello\nworld" → matches entire string
                  # Without s: "." doesn't match \n
```

**Unicode (`u`):**
```regex
/\p{L}+/u         # Match any Unicode letters
/\p{Sc}/u         # Match currency symbols: $, €, ¥, £
```

**Extended (`x`):**
```regex
/
  \d{3}           # Area code
  -               # Separator
  \d{3}           # Exchange
  -               # Separator
  \d{4}           # Number
/x                # Whitespace ignored, comments allowed
```

---

## Common Patterns

### Email Validation

```regex
# Simple
/^[a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/

# More comprehensive
/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/

# RFC 5322 compliant (complex)
/^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/i
```

**Examples:**
- Matches: `user@example.com`, `john.doe@company.co.uk`
- May match: `test@test.t` (2 letter TLD)

---

### URL Validation

```regex
# Basic HTTP/HTTPS URL
/^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/

# Simple version
/^https?:\/\/[^\s]+$/

# With optional protocol
/^(https?:\/\/)?(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}.*$/
```

**Examples:**
- Matches: `https://example.com`, `http://www.site.org/path`

---

### Phone Numbers

```regex
# US format: (123) 456-7890
/^\(\d{3}\)\s*\d{3}-\d{4}$/

# US format: 123-456-7890
/^\d{3}-\d{3}-\d{4}$/

# Flexible US format
/^(\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$/

# International format
/^\+?[1-9]\d{1,14}$/
```

**Examples:**
- Matches: `(123) 456-7890`, `123-456-7890`, `+1-123-456-7890`

---

### IP Address

```regex
# IPv4
/^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/

# Simplified IPv4
/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/

# IPv6 (basic)
/^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$/
```

**Examples:**
- Matches: `192.168.1.1`, `10.0.0.1`, `255.255.255.255`

---

### Date Formats

```regex
# YYYY-MM-DD
/^\d{4}-\d{2}-\d{2}$/

# MM/DD/YYYY
/^\d{2}\/\d{2}\/\d{4}$/

# DD-MM-YYYY or DD/MM/YYYY
/^\d{2}[-\/]\d{2}[-\/]\d{4}$/

# ISO 8601 datetime
/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$/
```

**Examples:**
- Matches: `2024-01-15`, `01/15/2024`, `15-01-2024`

---

### Credit Card

```regex
# Visa
/^4[0-9]{12}(?:[0-9]{3})?$/

# MasterCard
/^5[1-5][0-9]{14}$/

# American Express
/^3[47][0-9]{13}$/

# General (with optional spaces/dashes)
/^[\d\s-]{13,19}$/
```

**Examples:**
- Matches: `4111111111111111`, `5500-0000-0000-0004`

---

### Password Strength

```regex
# At least 8 characters, one uppercase, one lowercase, one digit
/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/

# At least 8 characters, uppercase, lowercase, digit, special char
/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/

# Complex: 12+ chars, all character types
/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{12,}$/
```

---

### Username

```regex
# Alphanumeric, 3-16 characters
/^[a-zA-Z0-9]{3,16}$/

# Allow underscore and hyphen
/^[a-zA-Z0-9_-]{3,16}$/

# Must start with letter
/^[a-zA-Z][a-zA-Z0-9_-]{2,15}$/
```

**Examples:**
- Matches: `user123`, `john_doe`, `alice-wonderland`

---

### HTML Tags

```regex
# Opening tag
/<[a-z]+[^>]*>/i

# Closing tag
/<\/[a-z]+>/i

# Opening and closing with content
/<([a-z]+)[^>]*>.*?<\/\1>/i

# Self-closing tag
/<[a-z]+[^>]*\/>/i

# Any HTML tag
/<\/?[a-z][a-z0-9]*[^<>]*>/i
```

**Examples:**
- Matches: `<div>`, `<span class="test">`, `</div>`, `<br />`

---

### Hex Color

```regex
# 3 or 6 digit hex
/^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$/

# Only 6 digit
/^#[a-fA-F0-9]{6}$/

# With or without #
/^#?[a-fA-F0-9]{6}$/
```

**Examples:**
- Matches: `#FF0000`, `#f00`, `FF0000`

---

### File Extension

```regex
# Image files
/\.(jpg|jpeg|png|gif|bmp|svg)$/i

# Document files
/\.(pdf|doc|docx|txt|rtf)$/i

# Any extension
/\.([a-zA-Z0-9]+)$/

# Multiple extensions
/\.tar\.gz$/
```

**Examples:**
- Matches: `file.jpg`, `document.pdf`, `archive.tar.gz`

---

### Social Security Number (US)

```regex
# SSN format: 123-45-6789
/^\d{3}-\d{2}-\d{4}$/

# SSN with or without dashes
/^\d{3}-?\d{2}-?\d{4}$/
```

**Examples:**
- Matches: `123-45-6789`, `123456789`

---

### ZIP Code (US)

```regex
# 5 digits
/^\d{5}$/

# 5 or 9 digits (ZIP+4)
/^\d{5}(-\d{4})?$/
```

**Examples:**
- Matches: `12345`, `12345-6789`

---

### Currency

```regex
# USD format
/^\$\d{1,3}(,\d{3})*(\.\d{2})?$/

# General currency
/^[\$£€]\d+(\.\d{2})?$/

# With optional cents
/^\$?\d+(,\d{3})*(\.\d{2})?$/
```

**Examples:**
- Matches: `$1,234.56`, `£99.99`, `$1000`

---

## Language-Specific Syntax

### Python

```python
import re

# Match
match = re.match(r'pattern', string)
match = re.search(r'pattern', string)
matches = re.findall(r'pattern', string)

# Replace
result = re.sub(r'pattern', 'replacement', string)

# Split
parts = re.split(r'pattern', string)

# Compile (for reuse)
pattern = re.compile(r'\d+')
match = pattern.search(string)

# Named groups
match = re.search(r'(?P<year>\d{4})-(?P<month>\d{2})', '2024-01')
year = match.group('year')  # '2024'

# Flags
re.search(r'pattern', string, re.IGNORECASE)
re.search(r'pattern', string, re.MULTILINE | re.DOTALL)
```

---

### JavaScript

```javascript
// Literal notation
const regex = /pattern/flags;
const regex = /\d+/g;

// Constructor
const regex = new RegExp('pattern', 'flags');
const regex = new RegExp('\\d+', 'g');

// Test (boolean)
regex.test(string);       // true or false
/\d+/.test('123');        // true

// Match
string.match(regex);      // Array of matches or null
'hello 123'.match(/\d+/); // ['123']

// Replace
string.replace(regex, replacement);
'hello world'.replace(/world/, 'there'); // 'hello there'

// Split
string.split(regex);
'a,b;c'.split(/[,;]/);    // ['a', 'b', 'c']

// Named groups
const match = /(?<year>\d{4})-(?<month>\d{2})/.exec('2024-01');
match.groups.year;        // '2024'

// Global flag
const regex = /\d+/g;
const matches = [...string.matchAll(regex)];
```

---

### PHP

```php
// Match
preg_match('/pattern/', $string, $matches);
preg_match_all('/pattern/', $string, $matches);

// Replace
preg_replace('/pattern/', 'replacement', $string);

// Split
preg_split('/pattern/', $string);

// Named groups
preg_match('/(?P<year>\d{4})-(?P<month>\d{2})/', '2024-01', $matches);
echo $matches['year'];  // '2024'

// Modifiers (flags)
preg_match('/pattern/i', $string);    // Case-insensitive
preg_match('/pattern/m', $string);    // Multiline
preg_match('/pattern/s', $string);    // Dotall
```

---

### Java

```java
import java.util.regex.*;

// Compile pattern
Pattern pattern = Pattern.compile("pattern");
Pattern pattern = Pattern.compile("pattern", Pattern.CASE_INSENSITIVE);

// Match
Matcher matcher = pattern.matcher(string);
boolean found = matcher.find();
boolean matches = matcher.matches();

// Groups
if (matcher.find()) {
    String group = matcher.group(1);
}

// Replace
String result = pattern.matcher(string).replaceAll("replacement");

// Split
String[] parts = pattern.split(string);

// Named groups
Pattern pattern = Pattern.compile("(?<year>\\d{4})-(?<month>\\d{2})");
Matcher matcher = pattern.matcher("2024-01");
if (matcher.find()) {
    String year = matcher.group("year");  // "2024"
}
```

---

### Ruby

```ruby
# Match
string.match(/pattern/)
string =~ /pattern/       # Returns position or nil

# Scan (find all)
string.scan(/pattern/)

# Replace
string.gsub(/pattern/, 'replacement')
string.sub(/pattern/, 'replacement')  # Replace first only

# Split
string.split(/pattern/)

# Named groups
/(?<year>\d{4})-(?<month>\d{2})/ =~ '2024-01'
year    # '2024'
month   # '01'

# Modifiers
/pattern/i               # Case-insensitive
/pattern/m               # Multiline
```

---

## Practical Examples

### Extract All Emails

```regex
/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g
```

**Text:**
```
Contact us at support@example.com or sales@company.org
```

**Matches:** `support@example.com`, `sales@company.org`

---

### Extract All URLs

```regex
/https?:\/\/[^\s]+/g
```

**Text:**
```
Visit https://example.com and http://test.org for more info
```

**Matches:** `https://example.com`, `http://test.org`

---

### Extract Hashtags

```regex
/#[a-zA-Z0-9_]+/g
```

**Text:**
```
Check out #programming and #coding_tips
```

**Matches:** `#programming`, `#coding_tips`

---

### Extract Mentions

```regex
/@[a-zA-Z0-9_]+/g
```

**Text:**
```
Thanks to @john_doe and @alice for help
```

**Matches:** `@john_doe`, `@alice`

---

### Validate Credit Card Format

```regex
/^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$/
```

**Matches:**
- `1234 5678 9012 3456`
- `1234-5678-9012-3456`
- `1234567890123456`

---

### Parse CSV Line

```regex
/(?:^|,)("(?:[^"]|"")*"|[^,]*)/g
```

**Text:**
```
John,Doe,"123 Main St, Apt 4",555-1234
```

**Matches:** `John`, `Doe`, `"123 Main St, Apt 4"`, `555-1234`

---

### Remove HTML Tags

```regex
/<[^>]*>/g
```

**Text:**
```html
<p>Hello <strong>world</strong></p>
```

**After replacement with empty string:** `Hello world`

---

### Find Duplicate Words

```regex
/\b(\w+)\s+\1\b/g
```

**Text:**
```
This is is a test test
```

**Matches:** `is is`, `test test`

---

### Extract Numbers from Text

```regex
/\d+(\.\d+)?/g
```

**Text:**
```
Price: $19.99, Quantity: 5, Total: 99.95
```

**Matches:** `19.99`, `5`, `99.95`

---

### Validate IPv4 Address

```regex
/^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
```

**Matches:** `192.168.1.1`, `10.0.0.255`
**Rejects:** `256.1.1.1`, `192.168.1`

---

### Extract Domain from Email

```regex
/@(.+)$/
```

**Text:** `user@example.com`
**Group 1:** `example.com`

---

### Camel Case to Snake Case

```regex
/([a-z])([A-Z])/g

# Replace with: $1_$2
# Then lowercase
```

**Text:** `camelCaseString`
**Result:** `camel_case_string`

---

## Best Practices

### 1. Keep It Simple

```regex
# Bad: Overly complex
/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/

# Good: Break into parts, validate separately
/^.{8,}$/                # Length
/[a-z]/                  # Lowercase
/[A-Z]/                  # Uppercase
/\d/                     # Digit
/[@$!%*?&]/             # Special char
```

---

### 2. Use Raw Strings (Python)

```python
# Bad: Double escaping
pattern = "\\d{3}-\\d{4}"

# Good: Raw string
pattern = r"\d{3}-\d{4}"
```

---

### 3. Compile for Reuse

```python
# Bad: Recompile every time
for item in items:
    if re.match('\d+', item):
        ...

# Good: Compile once
pattern = re.compile(r'\d+')
for item in items:
    if pattern.match(item):
        ...
```

---

### 4. Use Non-Capturing Groups

```regex
# Bad: Unnecessary capturing
/(cat|dog)s?/

# Good: Non-capturing when you don't need the group
/(?:cat|dog)s?/
```

---

### 5. Be Specific

```regex
# Bad: Too greedy
/.+/

# Good: Match what you need
/[a-zA-Z0-9]+/
/\w+/
```

---

### 6. Test Edge Cases

- Empty strings
- Very long strings
- Special characters
- Unicode characters
- Whitespace variations

---

### 7. Document Complex Patterns

```regex
# Verbose mode (Python, PCRE)
pattern = re.compile(r"""
    ^                 # Start of string
    (?=.*[a-z])       # At least one lowercase
    (?=.*[A-Z])       # At least one uppercase
    (?=.*\d)          # At least one digit
    .{8,}             # At least 8 characters
    $                 # End of string
""", re.VERBOSE)
```

---

### 8. Avoid Catastrophic Backtracking

```regex
# Bad: Can cause exponential backtracking
/(a+)+b/

# Good: Use possessive quantifiers or atomic groups
/(a++)b/              # Possessive (PCRE)
/(?>a+)b/             # Atomic group
```

---

### 9. Use Tools for Testing

**Online regex testers:**
- [regex101.com](https://regex101.com)
- [regexr.com](https://regexr.com)
- [regextester.com](https://www.regextester.com)

---

### 10. Validate, Don't Parse

```regex
# Good for validation
/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/

# Bad for parsing complex structures
# Use proper parsers for HTML, XML, JSON, etc.
```

---

## Common Mistakes

### 1. Not Escaping Special Characters

```regex
# Wrong: Trying to match literal dot
/file.txt/            # Matches: file.txt, fileXtxt, file_txt

# Correct
/file\.txt/           # Matches only: file.txt
```

---

### 2. Forgetting Anchors

```regex
# Wrong: Matches part of string
/\d{3}/               # "abc123def" matches

# Correct: Match entire string
/^\d{3}$/             # Only "123" matches
```

---

### 3. Greedy Quantifiers

```regex
# Wrong: Matches too much
/<div>.*<\/div>/      # "<div>a</div><div>b</div>" matches entire string

# Correct: Use lazy quantifier
/<div>.*?<\/div>/     # Matches "<div>a</div>" only
```

---

### 4. Not Using Word Boundaries

```regex
# Wrong: Matches partial words
/test/                # Matches "testing", "retest"

# Correct: Match whole word
/\btest\b/            # Matches only "test" as whole word
```

---

### 5. Case Sensitivity

```regex
# Wrong: Won't match uppercase
/hello/               # Doesn't match "Hello"

# Correct: Use case-insensitive flag
/hello/i              # Matches "hello", "Hello", "HELLO"
```

---

## Performance Tips

### 1. Anchor When Possible

```regex
# Slower
/\d{3}-\d{4}/

# Faster (if validating entire string)
/^\d{3}-\d{4}$/
```

---

### 2. Be Specific with Character Classes

```regex
# Slower
/.*/

# Faster
/[a-zA-Z0-9]*/
```

---

### 3. Avoid Unnecessary Captures

```regex
# Slower
/(cat|dog)/

# Faster (if you don't need the capture)
/(?:cat|dog)/
```

---

### 4. Use Atomic Groups for Non-Backtracking

```regex
# Can backtrack
/(ab)+/

# No backtracking (PCRE)
/(?>ab)+/
```

---

### 5. Limit Quantifier Range

```regex
# Slower (unbounded)
/\d+/

# Faster (if you know max length)
/\d{1,10}/
```

---

## Quick Reference

### Metacharacters

| Character | Meaning |
|-----------|---------|
| `.` | Any character (except newline) |
| `^` | Start of string/line |
| `$` | End of string/line |
| `*` | 0 or more |
| `+` | 1 or more |
| `?` | 0 or 1 (optional) |
| `\|` | Alternation (OR) |
| `()` | Capturing group |
| `[]` | Character class |
| `{}` | Quantifier |
| `\` | Escape character |

---

### Character Classes

| Class | Meaning |
|-------|---------|
| `\d` | Digit `[0-9]` |
| `\D` | Non-digit |
| `\w` | Word char `[a-zA-Z0-9_]` |
| `\W` | Non-word char |
| `\s` | Whitespace |
| `\S` | Non-whitespace |
| `.` | Any char (except newline) |

---

### Quantifiers

| Quantifier | Meaning |
|------------|---------|
| `*` | 0 or more |
| `+` | 1 or more |
| `?` | 0 or 1 |
| `{n}` | Exactly n |
| `{n,}` | n or more |
| `{n,m}` | Between n and m |
| `*?`, `+?`, `??` | Lazy versions |

---

### Anchors

| Anchor | Meaning |
|--------|---------|
| `^` | Start of string/line |
| `$` | End of string/line |
| `\b` | Word boundary |
| `\B` | Non-word boundary |
| `\A` | Start of string |
| `\Z` | End of string |

---

## See Also
- [[00 - Programming MOC]] - Programming overview
- [[Git]] - Version control (uses regex in grep)
- [[SQL]] - Database queries (supports regex in some DBs)
