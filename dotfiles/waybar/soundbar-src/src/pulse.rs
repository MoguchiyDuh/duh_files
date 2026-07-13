use libpulse_binding::context::{Context, FlagSet as ContextFlagSet, State as ContextState};
use libpulse_binding::mainloop::standard::{IterateResult, Mainloop};
use libpulse_binding::operation::{Operation, State as OperationState};
use libpulse_binding::volume::Volume;
use std::cell::RefCell;
use std::rc::Rc;
use std::thread;
use std::time::Duration;

/// Blocking-connect to the running PulseAudio-compatible server (PipeWire's
/// pulse shim included). Retries forever on failure so the daemon survives
/// the audio server restarting; waybar's own `restart-interval` is the outer
/// safety net if the process itself dies.
pub fn connect(app_name: &str) -> (Mainloop, Rc<RefCell<Context>>) {
    loop {
        if let Some(pair) = try_connect(app_name) {
            return pair;
        }
        thread::sleep(Duration::from_secs(2));
    }
}

fn try_connect(app_name: &str) -> Option<(Mainloop, Rc<RefCell<Context>>)> {
    let mut mainloop = Mainloop::new()?;
    let context = Rc::new(RefCell::new(Context::new(&mainloop, app_name)?));

    context
        .borrow_mut()
        .connect(None, ContextFlagSet::NOAUTOSPAWN, None)
        .ok()?;

    loop {
        match mainloop.iterate(true) {
            IterateResult::Quit(_) | IterateResult::Err(_) => return None,
            IterateResult::Success(_) => {}
        }
        let state = context.borrow().get_state();
        match state {
            ContextState::Ready => return Some((mainloop, context)),
            ContextState::Failed | ContextState::Terminated => return None,
            _ => {}
        }
    }
}

/// Blocks the mainloop until a pending introspection `Operation` finishes.
pub fn wait_op<T: ?Sized>(mainloop: &mut Mainloop, op: &Operation<T>) {
    while op.get_state() == OperationState::Running {
        mainloop.iterate(true);
    }
}

/// Converts a raw PulseAudio volume to a rounded 0-100+ percentage.
pub fn percent(volume: Volume) -> u32 {
    return ((volume.0 as f64 / Volume::NORMAL.0 as f64) * 100.0).round() as u32;
}
