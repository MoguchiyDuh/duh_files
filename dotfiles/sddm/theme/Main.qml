import QtQuick 2.0
import QtQuick.Effects
import SddmComponents 2.0

Rectangle {
    id: root

    Colors { id: theme }

    property string fontFamily: config.font ? config.font : "FiraCode Nerd Font"
    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property string message: ""
    property color messageColor: theme.muted
    property bool busy: false
    property string pendingAction: ""
    property bool sessionMenuOpen: false
    property bool capsLock: typeof keyboard !== "undefined" ? keyboard.capsLock : false
    readonly property bool multiLayout: typeof keyboard !== "undefined" && keyboard.layouts.length > 1
    readonly property string layoutName: multiLayout ? keyboard.layouts[keyboard.currentLayout].shortName.toUpperCase() : ""

    readonly property color cardColor: Qt.rgba(theme.surfaceContainer.r, theme.surfaceContainer.g, theme.surfaceContainer.b, 0.88)
    readonly property color fieldColor: Qt.rgba(theme.surfaceVariant.r, theme.surfaceVariant.g, theme.surfaceVariant.b, 0.45)
    readonly property color hoverColor: Qt.lighter(fieldColor, 1.35)
    readonly property color cornerColor: Qt.rgba(theme.surfaceContainer.r, theme.surfaceContainer.g, theme.surfaceContainer.b, 0.55)

    color: theme.surface

    function sessionName() {
        if (sessionModel.rowCount() === 0)
            return "Session"
        return sessionModel.data(sessionModel.index(sessionIndex, 0), Qt.UserRole + 4)
    }

    function cycleSession(step) {
        var n = sessionModel.count
        if (n > 0)
            sessionIndex = (sessionIndex + n + step) % n
    }

    function doLogin() {
        if (busy || user.text.length === 0)
            return
        busy = true
        message = ""
        sddm.login(user.text, password.text, sessionIndex)
    }

    function requestPower(action) {
        if (action === "suspend") {
            sddm.suspend()
            return
        }
        closePopups()
        pendingAction = action
        powerDialog.visible = true
        powerDialog.forceActiveFocus()
    }

    function closePopups() {
        powerDialog.visible = false
        sessionMenu.visible = false
        sessionMenuOpen = false
        pendingAction = ""
    }

    function confirmPower() {
        if (pendingAction === "reboot")
            sddm.reboot()
        else if (pendingAction === "poweroff")
            sddm.powerOff()
        closePopups()
    }

    function powerTitle() {
        if (pendingAction === "reboot")
            return "Restart the system?"
        if (pendingAction === "poweroff")
            return "Power off the system?"
        return ""
    }

    function powerHint() {
        if (pendingAction === "reboot")
            return "The session will end and the machine will restart."
        if (pendingAction === "poweroff")
            return "Any unsaved work in other sessions will be lost."
        return ""
    }

    function powerVerb() {
        if (pendingAction === "reboot")
            return "Restart"
        if (pendingAction === "poweroff")
            return "Power Off"
        return ""
    }

    component PowerButton: Rectangle {
        id: pwrBtn
        property string glyph
        property string label
        property color tint: theme.muted
        property bool danger: false
        signal activated()
        width: 46
        height: 46
        radius: 23
        color: pwrArea.pressed ? Qt.lighter(root.cornerColor, 1.4) : pwrArea.containsMouse ? root.hoverColor : root.cornerColor
        border.width: 1
        border.color: pwrArea.containsMouse ? Qt.rgba(theme.outline.r, theme.outline.g, theme.outline.b, 0.9) : Qt.rgba(theme.outline.r, theme.outline.g, theme.outline.b, 0.45)
        scale: pwrArea.pressed ? 0.9 : 1
        Behavior on color { ColorAnimation { duration: 120 } }
        Behavior on scale { NumberAnimation { duration: 90 } }

        Text {
            anchors.centerIn: parent
            text: pwrBtn.glyph
            color: pwrBtn.danger && pwrArea.containsMouse ? theme.error : pwrBtn.tint
            font.family: root.fontFamily
            font.pixelSize: 19
        }

        Text {
            id: pwrLabel
            anchors.bottom: parent.top
            anchors.bottomMargin: 8
            anchors.horizontalCenter: parent.horizontalCenter
            text: pwrBtn.label
            color: theme.foreground
            font.family: root.fontFamily
            font.pixelSize: 12
            font.weight: Font.Medium
            opacity: pwrArea.containsMouse ? 1 : 0
            Behavior on opacity { NumberAnimation { duration: 140 } }
        }

        MouseArea {
            id: pwrArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: pwrBtn.activated()
        }
    }

    Image {
        anchors.fill: parent
        source: config.background ? config.background : "background.png"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        onStatusChanged: if (status === Image.Error) visible = false
    }

    Rectangle {
        anchors.fill: parent
        color: "#000000"
        opacity: 0.35
    }

    Rectangle {
        id: overlayDim
        anchors.fill: parent
        visible: powerDialog.visible
        color: "#000000"
        opacity: visible ? 0.45 : 0
        Behavior on opacity { NumberAnimation { duration: 150 } }
    }

    MouseArea {
        anchors.fill: parent
        visible: powerDialog.visible || sessionMenu.visible
        enabled: visible
        onClicked: root.closePopups()
    }

    Connections {
        target: sddm
        function onLoginSucceeded() {
            root.busy = false
            root.messageColor = theme.primary
            root.message = "Welcome back"
        }
        function onLoginFailed() {
            root.busy = false
            password.text = ""
            root.messageColor = theme.error
            root.message = "Authentication failed"
            shake.restart()
            password.forceActiveFocus()
        }
        function onInformationMessage(msg) {
            root.busy = false
            root.messageColor = theme.muted
            root.message = msg
        }
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            var now = new Date()
            clock.text = Qt.formatTime(now, "HH:mm")
            date.text = Qt.formatDate(now, "dddd, MMMM dd").toUpperCase()
        }
    }

    SequentialAnimation {
        running: true
        NumberAnimation { target: hero; property: "opacity"; from: 0; to: 1; duration: 420; easing.type: Easing.OutQuad }
        NumberAnimation { target: card; property: "opacity"; from: 0; to: 1; duration: 380; easing.type: Easing.OutQuad }
        NumberAnimation { target: card; property: "anchors.verticalCenterOffset"; from: 130; to: 100; duration: 420; easing.type: Easing.OutCubic }
    }

    Column {
        id: hero
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: -200
        spacing: 2
        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowColor: "#8c000000"
            shadowBlur: 0.6
            shadowVerticalOffset: 3
        }

        Text {
            id: date
            anchors.horizontalCenter: parent.horizontalCenter
            color: theme.muted
            font.family: root.fontFamily
            font.pixelSize: 19
            font.weight: Font.Medium
            font.letterSpacing: 4
        }

        Text {
            id: clock
            anchors.horizontalCenter: parent.horizontalCenter
            color: theme.foreground
            font.family: root.fontFamily
            font.pixelSize: 150
            font.weight: Font.Bold
        }
    }

    Rectangle {
        id: card
        width: 420
        height: content.implicitHeight + 56
        radius: 16
        color: root.cardColor
        border.width: 1
        border.color: Qt.rgba(theme.outline.r, theme.outline.g, theme.outline.b, 0.5)
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: 100

        SequentialAnimation {
            id: shake
            NumberAnimation { target: card; property: "anchors.horizontalCenterOffset"; to: -14; duration: 55 }
            NumberAnimation { target: card; property: "anchors.horizontalCenterOffset"; to: 14; duration: 55 }
            NumberAnimation { target: card; property: "anchors.horizontalCenterOffset"; to: -9; duration: 55 }
            NumberAnimation { target: card; property: "anchors.horizontalCenterOffset"; to: 0; duration: 55 }
        }

        Column {
            id: content
            anchors.centerIn: parent
            width: parent.width - 56
            spacing: 14
            opacity: root.busy ? 0.6 : 1
            layer.enabled: opacity < 1
            Behavior on opacity { NumberAnimation { duration: 120 } }

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 6

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Welcome back,"
                    color: theme.muted
                    font.family: root.fontFamily
                    font.pixelSize: 15
                }

                TextInput {
                    id: user
                    anchors.verticalCenter: parent.verticalCenter
                    width: 140
                    text: userModel.lastUser
                    color: theme.primary
                    font.family: root.fontFamily
                    font.pixelSize: 15
                    font.weight: Font.DemiBold
                    selectionColor: theme.primary
                    selectedTextColor: theme.accentText
                    onAccepted: password.forceActiveFocus()
                    Keys.onEscapePressed: root.closePopups()

                    Text {
                        anchors.fill: parent
                        verticalAlignment: Text.AlignVCenter
                        text: "user"
                        color: theme.muted
                        font: user.font
                        visible: user.text.length === 0
                    }

                    Rectangle {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        height: 1
                        color: user.activeFocus ? theme.primary : Qt.rgba(theme.outline.r, theme.outline.g, theme.outline.b, 0.6)
                        Behavior on color { ColorAnimation { duration: 120 } }
                    }
                }
            }

            Rectangle {
                id: field
                width: parent.width
                height: 54
                radius: 16
                color: Qt.rgba(theme.outline.r, theme.outline.g, theme.outline.b, 0.35)

                Rectangle {
                    anchors.fill: parent
                    radius: parent.radius
                    opacity: password.activeFocus ? 1 : 0
                    Behavior on opacity { NumberAnimation { duration: 160 } }
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: theme.primary }
                        GradientStop { position: 1.0; color: theme.tertiary }
                    }
                }

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 2
                    radius: parent.radius - 2
                    color: theme.surfaceContainerHigh
                }

                TextInput {
                    id: password
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    anchors.rightMargin: chips.width + submitButton.width + 26
                    verticalAlignment: TextInput.AlignVCenter
                    echoMode: TextInput.Password
                    passwordCharacter: "\u25cf"
                    clip: true
                    color: theme.foreground
                    selectionColor: theme.primary
                    selectedTextColor: theme.accentText
                    font.family: root.fontFamily
                    font.pixelSize: 16
                    font.letterSpacing: 2
                    onAccepted: root.doLogin()
                    Keys.onEscapePressed: {
                        if (root.pendingAction) {
                            root.closePopups()
                            return
                        }
                        password.text = ""
                        root.message = ""
                    }

                    Text {
                        anchors.fill: parent
                        verticalAlignment: Text.AlignVCenter
                        text: "\udb80\udf3e  Enter password"
                        color: theme.muted
                        font.family: root.fontFamily
                        font.pixelSize: 15
                        visible: password.text.length === 0
                    }
                }

                Row {
                    id: chips
                    anchors.right: submitButton.left
                    anchors.rightMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 6

                    Rectangle {
                        visible: root.capsLock
                        width: capsText.implicitWidth + 18
                        height: 26
                        radius: 10
                        color: Qt.rgba(theme.tertiary.r, theme.tertiary.g, theme.tertiary.b, 0.18)

                        Text {
                            id: capsText
                            anchors.centerIn: parent
                            text: "\udb81\ude32 CAPS"
                            color: theme.tertiary
                            font.family: root.fontFamily
                            font.pixelSize: 11
                            font.weight: Font.Bold
                        }
                    }

                    Rectangle {
                        visible: root.multiLayout
                        width: layoutText.implicitWidth + 18
                        height: 26
                        radius: 10
                        color: Qt.rgba(theme.primary.r, theme.primary.g, theme.primary.b, 0.16)

                        Text {
                            id: layoutText
                            anchors.centerIn: parent
                            text: "\udb80\udf0c " + root.layoutName
                            color: theme.primary
                            font.family: root.fontFamily
                            font.pixelSize: 11
                            font.weight: Font.Bold
                        }
                    }
                }

                Rectangle {
                    id: submitButton
                    anchors.right: parent.right
                    anchors.rightMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    width: 38
                    height: 38
                    radius: 10
                    scale: submitArea.pressed ? 0.9 : 1
                    Behavior on scale { NumberAnimation { duration: 90 } }
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: submitArea.containsMouse ? Qt.lighter(theme.primary, 1.12) : theme.primary }
                        GradientStop { position: 1.0; color: submitArea.containsMouse ? Qt.lighter(theme.tertiary, 1.12) : theme.tertiary }
                    }

                    Text {
                        anchors.centerIn: parent
                        text: "\uf054"
                        color: theme.accentText
                        font.family: root.fontFamily
                        font.pixelSize: 16
                        font.weight: Font.Bold
                    }

                    MouseArea {
                        id: submitArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.doLogin()
                    }
                }
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                height: 16
                text: root.message
                color: root.messageColor
                font.family: root.fontFamily
                font.pixelSize: 12
                Behavior on opacity { NumberAnimation { duration: 150 } }
            }

            Item {
                width: parent.width
                height: sessionPill.height

                Rectangle {
                    id: sessionPill
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    width: 230
                    height: 38
                    radius: 12
                    color: pillArea.containsMouse ? root.hoverColor : root.fieldColor
                    border.width: 1
                    border.color: root.sessionMenuOpen ? theme.primary : Qt.rgba(theme.outline.r, theme.outline.g, theme.outline.b, 0.4)
                    Behavior on color { ColorAnimation { duration: 90 } }

                    Text {
                        anchors.fill: parent
                        anchors.leftMargin: 14
                        anchors.rightMargin: 30
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                        text: root.sessionName()
                        color: theme.foreground
                        font.family: root.fontFamily
                        font.pixelSize: 13
                    }

                    Text {
                        anchors.right: parent.right
                        anchors.rightMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        text: root.sessionMenuOpen ? "\uf077" : "\uf078"
                        color: theme.muted
                        font.family: root.fontFamily
                        font.pixelSize: 10
                    }

                    MouseArea {
                        id: pillArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (sessionMenu.visible) {
                                root.closePopups()
                                return
                            }
                            root.closePopups()
                            var pos = sessionPill.mapToItem(root, 0, 0)
                            sessionMenu.x = pos.x + sessionPill.width / 2 - sessionMenu.width / 2
                            sessionMenu.y = pos.y - sessionMenu.height - 10
                            sessionMenu.visible = true
                            root.sessionMenuOpen = true
                            sessionMenu.forceActiveFocus()
                        }
                        onWheel: wheel.angleDelta.y > 0 ? root.cycleSession(-1) : root.cycleSession(1)
                    }
                }
            }
        }
    }

    Rectangle {
        id: sessionMenu
        width: 260
        height: menuColumn.implicitHeight + 12
        radius: 14
        color: Qt.rgba(theme.surfaceContainerHigh.r, theme.surfaceContainerHigh.g, theme.surfaceContainerHigh.b, 0.97)
        border.width: 1
        border.color: Qt.rgba(theme.outline.r, theme.outline.g, theme.outline.b, 0.6)
        visible: false
        z: 20
        opacity: visible ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 120 } }

        function select(i) {
            root.sessionIndex = i
            root.closePopups()
        }

        Keys.onEscapePressed: root.closePopups()

        Column {
            id: menuColumn
            anchors.centerIn: parent
            width: parent.width - 12
            spacing: 2

            Repeater {
                model: sessionModel

                Rectangle {
                    width: menuColumn.width
                    height: 38
                    radius: 10
                    color: sessionRow.containsMouse ? root.hoverColor : "transparent"

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width - 50
                        elide: Text.ElideRight
                        text: sessionModel.data(sessionModel.index(index, 0), Qt.UserRole + 4)
                        color: index === root.sessionIndex ? theme.primary : theme.foreground
                        font.family: root.fontFamily
                        font.pixelSize: 13
                        font.weight: index === root.sessionIndex ? Font.DemiBold : Font.Normal
                    }

                    Text {
                        anchors.right: parent.right
                        anchors.rightMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        text: "\uf00c"
                        visible: index === root.sessionIndex
                        color: theme.primary
                        font.family: root.fontFamily
                        font.pixelSize: 12
                    }

                    MouseArea {
                        id: sessionRow
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: sessionMenu.select(index)
                    }
                }
            }
        }
    }

    Rectangle {
        id: powerDialog
        width: 340
        height: dialogContent.implicitHeight + 48
        radius: 18
        color: Qt.rgba(theme.surfaceContainerHigh.r, theme.surfaceContainerHigh.g, theme.surfaceContainerHigh.b, 0.97)
        border.width: 1
        border.color: Qt.rgba(theme.outline.r, theme.outline.g, theme.outline.b, 0.6)
        anchors.centerIn: parent
        anchors.verticalCenterOffset: 40
        visible: false
        z: 20
        opacity: visible ? 1 : 0
        scale: visible ? 1 : 0.95
        Behavior on opacity { NumberAnimation { duration: 120 } }
        Behavior on scale { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }

        Keys.onEscapePressed: root.closePopups()

        Column {
            id: dialogContent
            anchors.centerIn: parent
            width: parent.width - 48
            spacing: 16

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: root.powerTitle()
                color: theme.foreground
                font.family: root.fontFamily
                font.pixelSize: 17
                font.weight: Font.DemiBold
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                text: root.powerHint()
                color: theme.muted
                font.family: root.fontFamily
                font.pixelSize: 12
            }

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 12

                Rectangle {
                    width: 120
                    height: 40
                    radius: 12
                    color: cancelArea.containsMouse ? root.hoverColor : root.fieldColor
                    border.width: 1
                    border.color: Qt.rgba(theme.outline.r, theme.outline.g, theme.outline.b, 0.4)
                    Behavior on color { ColorAnimation { duration: 90 } }

                    Text {
                        anchors.centerIn: parent
                        text: "Cancel"
                        color: theme.foreground
                        font.family: root.fontFamily
                        font.pixelSize: 13
                    }

                    MouseArea {
                        id: cancelArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.closePopups()
                    }
                }

                Rectangle {
                    width: 120
                    height: 40
                    radius: 12
                    color: confirmArea.containsMouse ? Qt.lighter(theme.error, 1.15) : theme.error
                    scale: confirmArea.pressed ? 0.94 : 1
                    Behavior on color { ColorAnimation { duration: 90 } }
                    Behavior on scale { NumberAnimation { duration: 90 } }

                    Text {
                        anchors.centerIn: parent
                        text: root.powerVerb()
                        color: theme.errorText
                        font.family: root.fontFamily
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                    }

                    MouseArea {
                        id: confirmArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.confirmPower()
                    }
                }
            }
        }
    }

    Text {
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: 24
        anchors.bottomMargin: 22
        text: sddm.hostName
        color: theme.muted
        font.family: root.fontFamily
        font.pixelSize: 13
        opacity: 0.85
    }

    Row {
        id: powersRow
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.rightMargin: 24
        anchors.bottomMargin: 22
        spacing: 10

        PowerButton {
            visible: sddm.canHibernate
            glyph: "\uf252"
            label: "Hibernate"
            tint: theme.muted
            onActivated: sddm.hibernate()
        }

        PowerButton {
            visible: sddm.canSuspend
            glyph: "\uf186"
            label: "Suspend"
            tint: theme.muted
            onActivated: root.requestPower("suspend")
        }

        PowerButton {
            visible: sddm.canReboot
            glyph: "\uf021"
            label: "Restart"
            tint: theme.muted
            onActivated: root.requestPower("reboot")
        }

        PowerButton {
            visible: sddm.canPowerOff
            glyph: "\uf011"
            label: "Power Off"
            tint: theme.error
            danger: true
            onActivated: root.requestPower("poweroff")
        }
    }

    Component.onCompleted: {
        if (user.text.length === 0)
            user.forceActiveFocus()
        else
            password.forceActiveFocus()
    }
}
