# QML Worked Examples

!!! abstract "In a nutshell"
    Worked QML snippets for common legacy skill-display patterns: Lottie animations, sliding images, paginated text, card list views, proportional/auto-fit layouts, slideshows, event handling, and resting (idle) faces. For the QML concepts and design guidelines these examples build on, see [Mycroft-GUI QT5](qt5-gui.md).

!!! danger "The OVOS GUI is deprecated: see [Screens on OVOS Today](gui-status.md) for the full picture"
    These examples target the legacy Qt5/QML client. There is no generally usable OVOS GUI,
    and a replacement is **Upcoming**. See [GUI Adapters](gui-adapters.md) for the rework.

---

## Advanced skill displays using QML

**Display Lottie Animations**:

You can use the `LottieAnimation` item just like any other `QtQuick` element, such as an `Image` and place it in your scene any way you please.

**QML Example**

```qml
// standard imports (QtQuick, QtQuick.Controls, QtQuick.Layouts, Kirigami, Mycroft, see the imports block above)
import org.kde.lottie 1.0

Mycroft.Delegate {
    LottieAnimation {     
        id: fancyAnimation 
        anchors.fill: parent
        source: Qt.resolvedUrl("animations/fancy_animation.json")
        loops: Animation.Infinite
        fillMode: Image.PreserveAspectFit    
        running: true
    }    
}

```

**Display Sliding Images**

Contains an image that scrolls slowly so it can be shown completely.

**QML Example**

```qml
// standard imports (QtQuick, QtQuick.Controls, QtQuick.Layouts, Kirigami, Mycroft, see the imports block above)

Mycroft.Delegate {
     background: Mycroft.SlidingImage {
     source: "foo.jpg" 
     running: bool    //If true the sliding animation is active
     speed: 1         //Animation speed in Kirigami.Units.gridUnit / second
   }
}

```

**Display Paginated Text**

Takes a long text and breaks it down into pages that can be horizontally swiped

**QML Example**

```qml
// standard imports (QtQuick, QtQuick.Controls, QtQuick.Layouts, Kirigami, Mycroft, see the imports block above)

Mycroft.Delegate {
     Mycroft.PaginatedText {
         text: string      //The text that should be displayed
         currentIndex: 0   //The currently visible page number (starting from 0)
     }
}

```

**Display A Vertical ListView With Information Cards**

Kirigami CardsListView is a ListView that can have AbstractCard as its delegate. It automatically assigns the proper spacing and margins around the cards, following the design guidelines.

**Python Skill Example**

```python
...
def handle_food_places(self, message):
...
self.gui["foodPlacesBlob"] = results.json
self.gui.show_page("foodplaces.qml")
...

```

**QML Example**

```qml
// standard imports (QtQuick, QtQuick.Controls, QtQuick.Layouts, Kirigami, Mycroft, see the imports block above)

Mycroft.Delegate{
    id: root
    property var foodPlacesModel: sessionData.foodPlacesBlob

    Kirigami.CardsListView {
        id: restaurantsListView
        Layout.fillWidth: true
        Layout.fillHeight: true
        model: foodPlacesModel
        delegate: Kirigami.AbstractCard {
            id: rootCard
            implicitHeight: delegateItem.implicitHeight + Kirigami.Units.largeSpacing
            contentItem: Item {
                implicitWidth: parent.implicitWidth
                implicitHeight: parent.implicitHeight
                ColumnLayout {
                    id: delegateItem
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    spacing: Kirigami.Units.smallSpacing
                    Kirigami.Heading {
                        id: restaurantNameLabel
                        Layout.fillWidth: true
                        text: modelData.name
                        level: 3
                        wrapMode: Text.WordWrap
                    }
                    Kirigami.Separator {
                        Layout.fillWidth: true
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.preferredHeight: form.implicitHeight
                        Image {
                            id: placeImage
                            source: modelData.image
                            Layout.fillHeight: true
                            Layout.preferredWidth: placeImage.implicitHeight + Kirigami.Units.gridUnit * 2
                            fillMode: Image.PreserveAspectFit
                        }
                        Kirigami.Separator {
                            Layout.fillHeight: true
                        }
                        Kirigami.FormLayout {
                            id: form
                            Layout.fillWidth: true
                            Layout.minimumWidth: aCard.implicitWidth
                            Layout.alignment: Qt.AlignLeft | Qt.AlignBottom
                            Label {
                                Kirigami.FormData.label: "Description:"
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                                elide: Text.ElideRight
                                text: modelData.restaurantDescription
                            }
                            Label {
                                Kirigami.FormData.label: "Phone:"
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                                elide: Text.ElideRight
                                text: modelData.phone
                            }
                        }
                    }
                }
            }
        }
    }
}

```

**Using Proportional Delegate For Simple Display Skills & Auto Layout**

**ProportionalDelegate** is a delegate which has proportional padding and a columnlayout as mainItem. The delegate supports a `proportionalGridUnit`, based on its size. Contents should scale proportionally to the delegate size, either directly or by using the `proportionalGridUnit`.

**AutoFitLabel** is a label that will always scale its text size according to the item size rather than the other way around

**QML Example**

```qml
// standard imports (QtQuick, QtQuick.Controls, QtQuick.Layouts, Kirigami, Mycroft, see the imports block above)

Mycroft.ProportionalDelegate {
    id: root

    Mycroft.AutoFitLabel {
        id: monthLabel
        font.weight: Font.Bold
        Layout.fillWidth: true
        Layout.preferredHeight: proportionalGridUnit * 40
        text: sessionData.month
    }

    Mycroft.AutoFitLabel {
        id: dayLabel
        font.weight: Font.Bold
        Layout.fillWidth: true
        Layout.preferredHeight: proportionalGridUnit * 40
        text: sessionData.day
    }
}

```

**Using Slideshow Component To Show Cards Slideshow**

The Slideshow component lets you insert a slideshow with your custom delegate in any skill display. It can be tuned to autoplay and loop, and can also be scrolled or flicked manually by the user.

**QML Example**

```qml
// standard imports (QtQuick, QtQuick.Controls, QtQuick.Layouts, Kirigami, Mycroft, see the imports block above)

Mycroft.Delegate {
    id: root

    Mycroft.SlideShow {
        id: simpleSlideShow 
        model: sessionData.exampleModel // model with slideshow data
        anchors.fill: parent
        interval: 5000 // time to switch between slides 
        running: true // can be set to false if one wants to swipe manually
        loop: true // can be set to play through continously or just once
        delegate: Kirigami.AbstractCard { 
            width: rootItem.width
            height: rootItem.height
            contentItem: ColumnLayout {
                anchors.fill: parent
                Kirigami.Heading {
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    level: 3
                    text: modelData.Title
                }
                Kirigami.Separator {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1
                }
                Image {
                    Layout.fillWidth: true
                    Layout.preferredHeight: rootItem.height / 4
                    source: modelData.Image
                    fillMode: Image.PreserveAspectCrop
                }
            }
        }
    }
}

```

#### Event Handling

Mycroft GUI API provides an Event Handling Protocol between the skill and QML display. It lets skill authors forward events in either direction to an event consumer. Skill authors can create any number of custom events. Event names that start with "system." are available to all skills, like previous/next/pick.

**Simple Event Trigger Example From QML Display To Skill**

**Python Skill Example**

```python
    def initialize(self):
    # Initialize...
        self.gui.register_handler('skill.foo.event', self.handle_foo_event)
...
    def handle_foo_event(self, message):
        self.speak(message.data["string"])
...
...

```

**QML Example**

```qml
// standard imports (QtQuick, QtQuick.Controls, QtQuick.Layouts, Kirigami, Mycroft, see the imports block above)

Mycroft.Delegate {
    id: root

    Button {
        anchors.fill: parent
        text: "Click Me"
        onClicked: {
            triggerGuiEvent("skill.foo.event", {"string": "Lorem ipsum dolor sit amet"})
        }
    }
}

```

**Simple Event Trigger Example From Skill To QML Display**

**Python Skill Example**

```python
...
    def handle_foo_intent(self, message):
        self.gui['foobar'] = message.data.get("utterance")
        self.gui['color'] = "blue"
        self.gui.show_page("foo")
...
...

```

**QML Example**

```qml
// standard imports (QtQuick, QtQuick.Controls, QtQuick.Layouts, Kirigami, Mycroft, see the imports block above)

Mycroft.Delegate {
    id: root
    property var fooString: sessionData.foobar

    onFooStringChanged: {
        fooRect.color = sessionData.color 
    }

    Rectangle {
        id: fooRect
        anchors.fill: parent
        color: "#fff"
    }
}

```


#### Resting Faces

The resting face API lets skill authors extend their skills to supply their own custom IDLE screens, displayed when there is no activity on the screen.

**Simple Idle Screen Example**

**Python Skill Example**

```python
from ovos_workshop.decorators import resting_screen_handler
...
@resting_screen_handler('NameOfIdleScreen')
def handle_idle(self, message):
    self.gui.clear()
    self.log.info('Activating foo/bar resting page')
    self.gui["exampleText"] = "This Is A Idle Screen"
    self.gui.show_page('idle.qml')

```

**QML Example**

```qml
// standard imports (QtQuick, QtQuick.Controls, QtQuick.Layouts, Kirigami, Mycroft, see the imports block above)

Mycroft.Delegate {
    id: root
    property var fooString: sessionData.exampleText

    Kirigami.Heading {
        id: headerExample
        anchors.centerIn: parent
        text: fooString 
    }
}

```


---
**Read next:** [Home Screen](homescreen.md)
**Related:** [Mycroft-GUI QT5](qt5-gui.md) · [OVOS Shell](ovos-shell.md) · [GUI Protocol](gui-protocol.md) · [Screens on OVOS Today](gui-status.md)
