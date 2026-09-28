import QtQuick 2.0

QtObject {
    readonly property color background: "{{ colors.surface.default.hex }}"
    readonly property color surface: "{{ colors.surface.default.hex }}"
    readonly property color surfaceContainer: "{{ colors.surface_container.default.hex }}"
    readonly property color surfaceContainerHigh: "{{ colors.surface_container_high.default.hex }}"
    readonly property color surfaceContainerHighest: "{{ colors.surface_container_highest.default.hex }}"
    readonly property color surfaceVariant: "{{ colors.surface_variant.default.hex }}"
    readonly property color foreground: "{{ colors.on_surface.default.hex }}"
    readonly property color muted: "{{ colors.on_surface_variant.default.hex }}"
    readonly property color primary: "{{ colors.primary.default.hex }}"
    readonly property color accentText: "{{ colors.on_primary.default.hex }}"
    readonly property color primaryContainer: "{{ colors.primary_container.default.hex }}"
    readonly property color secondary: "{{ colors.secondary.default.hex }}"
    readonly property color tertiary: "{{ colors.tertiary.default.hex }}"
    readonly property color error: "{{ colors.error.default.hex }}"
    readonly property color errorText: "{{ colors.on_error.default.hex }}"
    readonly property color outline: "{{ colors.outline.default.hex }}"
}
