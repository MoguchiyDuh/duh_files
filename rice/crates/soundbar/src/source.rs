use crate::emit;
use crate::pulse::{self, wait_op};
use libpulse_binding::callbacks::ListResult;
use libpulse_binding::context::Context;
use libpulse_binding::context::subscribe::InterestMaskSet;
use libpulse_binding::mainloop::standard::Mainloop;
use std::cell::{Cell, RefCell};
use std::rc::Rc;

pub fn run() -> ! {
    let (mut mainloop, context) = pulse::connect("soundbar-source");

    let dirty = Rc::new(Cell::new(true));
    {
        let dirty = dirty.clone();
        context.borrow_mut().set_subscribe_callback(Some(Box::new(
            move |_facility, _operation, _index| {
                dirty.set(true);
            },
        )));
    }
    {
        let mask =
            InterestMaskSet::SOURCE | InterestMaskSet::SOURCE_OUTPUT | InterestMaskSet::SERVER;
        let op = context.borrow_mut().subscribe(mask, |_success| {});
        wait_op(&mut mainloop, &op);
    }

    loop {
        if dirty.replace(false) {
            render(&mut mainloop, &context);
        }
        mainloop.iterate(true);
    }
}

struct SourceSnapshot {
    index: u32,
    description: String,
    percent: u32,
    mute: bool,
}

fn render(mainloop: &mut Mainloop, context: &Rc<RefCell<Context>>) {
    let Some(source_name) = default_source_name(mainloop, context) else {
        return;
    };
    let Some(snapshot) = source_info(mainloop, context, &source_name) else {
        return;
    };
    let mic_active = has_active_capture(mainloop, context, snapshot.index);

    let icon = if snapshot.mute {
        '\u{f131}'
    } else {
        '\u{f130}'
    };
    let text = format!("{icon} {}%", snapshot.percent);

    // Compact by design: no "Input"/"Level" rows, just the device name as the
    // title and the click/scroll hints -- everything else lives in the color.
    let mut classes: Vec<&str> = Vec::new();
    if mic_active {
        classes.push("mic-active");
    }
    if snapshot.mute {
        classes.push("muted");
    }

    emit::emit(
        &text,
        &snapshot.description,
        &[],
        "LMB  Mixer\nRMB  Mute\nScroll  Adjust",
        &classes,
    );
}

fn default_source_name(mainloop: &mut Mainloop, context: &Rc<RefCell<Context>>) -> Option<String> {
    let result = Rc::new(RefCell::new(None));
    let op = {
        let result = result.clone();
        context.borrow().introspect().get_server_info(move |info| {
            *result.borrow_mut() = info.default_source_name.as_ref().map(|s| s.to_string());
        })
    };
    wait_op(mainloop, &op);
    return result.borrow_mut().take();
}

fn source_info(
    mainloop: &mut Mainloop,
    context: &Rc<RefCell<Context>>,
    name: &str,
) -> Option<SourceSnapshot> {
    let result = Rc::new(RefCell::new(None));
    let op = {
        let result = result.clone();
        context
            .borrow()
            .introspect()
            .get_source_info_by_name(name, move |item| {
                if let ListResult::Item(info) = item {
                    *result.borrow_mut() = Some(SourceSnapshot {
                        index: info.index,
                        description: info
                            .description
                            .as_ref()
                            .map(|d| d.to_string())
                            .unwrap_or_else(|| "Microphone".to_string()),
                        percent: pulse::percent(info.volume.avg()),
                        mute: info.mute,
                    });
                }
            })
    };
    wait_op(mainloop, &op);
    return result.borrow_mut().take();
}

/// True when at least one uncorked (actively capturing, not paused) stream
/// is reading from the given source -- the visual "mic in use" signal.
fn has_active_capture(
    mainloop: &mut Mainloop,
    context: &Rc<RefCell<Context>>,
    source_index: u32,
) -> bool {
    let result = Rc::new(Cell::new(false));
    let op = {
        let result = result.clone();
        context
            .borrow()
            .introspect()
            .get_source_output_info_list(move |item| {
                if let ListResult::Item(info) = item
                    && info.source == source_index
                    && !info.corked
                {
                    result.set(true);
                }
            })
    };
    wait_op(mainloop, &op);
    return result.get();
}
