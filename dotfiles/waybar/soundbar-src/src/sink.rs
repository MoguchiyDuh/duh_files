use crate::emit;
use crate::pulse::{self, wait_op};
use libpulse_binding::callbacks::ListResult;
use libpulse_binding::context::Context;
use libpulse_binding::context::subscribe::InterestMaskSet;
use libpulse_binding::mainloop::standard::Mainloop;
use std::cell::{Cell, RefCell};
use std::rc::Rc;

pub fn run() -> ! {
    let (mut mainloop, context) = pulse::connect("soundbar-sink");

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
        let mask = InterestMaskSet::SINK | InterestMaskSet::SINK_INPUT | InterestMaskSet::SERVER;
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

struct SinkSnapshot {
    index: u32,
    description: String,
    percent: u32,
    mute: bool,
}

fn render(mainloop: &mut Mainloop, context: &Rc<RefCell<Context>>) {
    let Some(sink_name) = default_sink_name(mainloop, context) else {
        return;
    };
    let Some(snapshot) = sink_info(mainloop, context, &sink_name) else {
        return;
    };
    let apps = sink_input_apps(mainloop, context, snapshot.index);

    let icon = if snapshot.mute {
        '\u{eee8}'
    } else if snapshot.percent >= 67 {
        '\u{f028}'
    } else if snapshot.percent >= 34 {
        '\u{f027}'
    } else {
        '\u{f026}'
    };
    let text = format!("{icon} {}%", snapshot.percent);

    let mut fields: Vec<(String, String)> =
        vec![("Level".to_string(), format!("{}%", snapshot.percent))];
    for (name, percent) in &apps {
        fields.push((name.clone(), format!("{percent}%")));
    }

    let classes: &[&str] = if snapshot.mute { &["muted"] } else { &[] };
    emit::emit(
        &text,
        &snapshot.description,
        &fields,
        "LMB  Mixer\nRMB  Mute\nScroll  Adjust",
        classes,
    );
}

fn default_sink_name(mainloop: &mut Mainloop, context: &Rc<RefCell<Context>>) -> Option<String> {
    let result = Rc::new(RefCell::new(None));
    let op = {
        let result = result.clone();
        context.borrow().introspect().get_server_info(move |info| {
            *result.borrow_mut() = info.default_sink_name.as_ref().map(|s| s.to_string());
        })
    };
    wait_op(mainloop, &op);
    return result.borrow_mut().take();
}

fn sink_info(
    mainloop: &mut Mainloop,
    context: &Rc<RefCell<Context>>,
    name: &str,
) -> Option<SinkSnapshot> {
    let result = Rc::new(RefCell::new(None));
    let op = {
        let result = result.clone();
        context
            .borrow()
            .introspect()
            .get_sink_info_by_name(name, move |item| {
                if let ListResult::Item(info) = item {
                    *result.borrow_mut() = Some(SinkSnapshot {
                        index: info.index,
                        description: info
                            .description
                            .as_ref()
                            .map(|d| d.to_string())
                            .unwrap_or_else(|| "Speakers".to_string()),
                        percent: pulse::percent(info.volume.avg()),
                        mute: info.mute,
                    });
                }
            })
    };
    wait_op(mainloop, &op);
    return result.borrow_mut().take();
}

fn sink_input_apps(
    mainloop: &mut Mainloop,
    context: &Rc<RefCell<Context>>,
    sink_index: u32,
) -> Vec<(String, u32)> {
    let result: Rc<RefCell<Vec<(String, u32)>>> = Rc::new(RefCell::new(Vec::new()));
    let op = {
        let result = result.clone();
        context
            .borrow()
            .introspect()
            .get_sink_input_info_list(move |item| {
                if let ListResult::Item(info) = item {
                    if info.sink == sink_index {
                        let name = info
                            .proplist
                            .get_str("application.name")
                            .unwrap_or_else(|| "App".to_string());
                        result
                            .borrow_mut()
                            .push((name, pulse::percent(info.volume.avg())));
                    }
                }
            })
    };
    wait_op(mainloop, &op);
    return result.borrow().clone();
}
