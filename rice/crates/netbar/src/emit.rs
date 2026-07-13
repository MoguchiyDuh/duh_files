use serde::Serialize;
use std::io::{self, Write};

#[derive(Serialize)]
struct Payload<'a> {
    text: &'a str,
    tooltip: &'a str,
    class: &'a [&'a str],
}

/// Emit one waybar custom-module JSON line: bold title, aligned "Label  value"
/// rows, an optional freeform block (secondary interfaces, proxy info -- rows
/// that don't fit the label/value table shape), a blank separator, then a
/// hint. Flushed immediately (NDJSON stream, not one-shot exec).
pub fn emit(
    text: &str,
    title: &str,
    fields: &[(String, String)],
    extra: &[String],
    hint: &str,
    classes: &[&str],
) {
    let width = fields
        .iter()
        .map(|(label, _)| label.chars().count())
        .max()
        .unwrap_or(0);
    let mut rows: Vec<String> = Vec::with_capacity(fields.len() + extra.len() + 4);
    rows.push(format!("<b>{}</b>", escape(title)));
    for (label, value) in fields {
        rows.push(format!("{label:<width$}  {}", escape(value)));
    }
    if !extra.is_empty() {
        rows.push(String::new());
        for line in extra {
            rows.push(line.clone());
        }
    }
    rows.push(String::new());
    rows.push(escape(hint));
    let tooltip = format!("<tt>{}</tt>", rows.join("\n"));
    write_payload(text, &tooltip, classes);
}

fn write_payload(text: &str, tooltip: &str, classes: &[&str]) {
    let payload = Payload {
        text,
        tooltip,
        class: classes,
    };
    let mut stdout = io::stdout();
    if serde_json::to_writer(&mut stdout, &payload).is_ok() {
        let _ = stdout.write_all(b"\n");
        let _ = stdout.flush();
    }
}

fn escape(text: &str) -> String {
    return text
        .replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;");
}
