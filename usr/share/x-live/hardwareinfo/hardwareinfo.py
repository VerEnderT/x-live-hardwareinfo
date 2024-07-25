import sys
import subprocess
import textwrap
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QSplitter, QHBoxLayout, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


#####                                      ##
# abhängigkeiten python3 python3-pyqt5 lshw #
##                                      #####


class LshwTreeWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("X-Live HardwareInfo")
        faktor = app.desktop().height()/780
        breite = int(750 * faktor)
        hoehe = int(500 * faktor)
        bts=int(16 * faktor)
        sts=int(14 * faktor)
        self.faktor = faktor
        xpos=int(150*faktor)
        ypos=int(170*faktor)
        self.setGeometry(xpos, ypos, breite, hoehe)
        self.setWindowIcon(QIcon.fromTheme("hardware"))
      
        self.style=str("""
            QWidget {
            background-color: #23252e;
            color: white;
            }
            QCheckBox:Indicator:Checked {
            border: 2px solid white;
            border-radius: """ + str(int(sts/2)) + """px;
            background-color: green;
            
            }
            QCheckBox:Indicator:Unchecked {
            border: 2px solid white;
            background-color: #23252e;
            }
            QPushButton {
            font-size: """ + str(sts) + """px; 
            text-align: centre;      
            border-radius: """+ str(int(8*self.faktor))+""";
            background-color: #33353e;
            border: 2px solid #33353e;
            padding-top: 2px;
            padding-left: 5px;
            padding-right: 5px;
            padding-bottom: 2px;
            color: white;
            }
            QLabel {
            font-size: """ + str(int(sts*1.2)) + """px; 
            text-align: centre;      
            border-radius: """+ str(int(8*self.faktor))+""";
            background: rgba(180,180, 180, 40);
            padding-top: 10px;
            padding-left: 10px;
            margin-left: 10px;  
            border: 0px solid #333333;
            color: white;
            }
            QTreeWidget {
            font-size: """ + str(int(sts*0.8)) + """px; 
            text-align: centre;      
            border-radius: """+ str(int(8*self.faktor))+""";
            background: rgba(180,180, 180, 240);
            padding-top: 10px;
            padding-left: 10px;
            border: 1px solid #aaaaaa;
            color: black;
            }
            QTextEdit {
            font-size: """ + str(sts) + """px; 
            text-align: centre;   
            padding-top: 10px;
            padding-left: 10px;   
            margin-left: 10px; 
            margin-top: 5px;    
            border-radius: """+ str(int(8*self.faktor))+""";
            background: rgba(0,0, 0, 70);
            border: 0px solid #aaaaaa;
            color: white;
            }
            QPushButton:hover {
            font-size: """ + str(int(int(sts)/14*16)) + """px;  
            background-color: #1b1b1b;
            border: 2px solid #1b1b1b;
            }
            """)
        
            
        self.setStyleSheet(self.style)
        layout = QVBoxLayout(self)

        self.splitter_main = QSplitter(Qt.Horizontal, self)
        layout.addWidget(self.splitter_main)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([" "])
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self.on_item_clicked)

        self.splitter_main.addWidget(self.tree)

        self.info_splitter = QSplitter(Qt.Vertical)
        self.splitter_main.addWidget(self.info_splitter)
        
        self.basic_info_label = QLabel("System Information")
        self.basic_info_label.setWordWrap(True)
        self.basic_info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align text to top and left
        self.info_splitter.addWidget(self.basic_info_label)
        
        self.item_info_label = QTextEdit(" ")
        self.item_info_label.setWordWrapMode(True)
        self.item_info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align text to top and left
        self.info_splitter.addWidget(self.item_info_label)

        # Set the stretch factors
        self.info_splitter.setStretchFactor(0, 1)  # 30% of the height
        self.info_splitter.setStretchFactor(1, 10)  # 70% of the height

        self.splitter_main.setStretchFactor(0, 5)  # 50% of the width for tree
        self.splitter_main.setStretchFactor(1, 5)  # 50% of the width for info

        self.setLayout(layout)

        self.lshw = ""
        self.load_lshw_data()
        self.set_basicinfo()

    def load_lshw_data(self):
        # Execute lshw command and parse output
        cmd = 'sudo lshw'.split(" ")
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.lshw = result.stdout
        lshw_output = self.lshw.splitlines()

        # Initialize structures
        counter = [0] * 10  # Adjust size as needed based on expected depth
        items = []

        for line in lshw_output:
            if "*-" in line:
                row = (line.find("*") + 1) // 3 - 1
                counter[row] += 1
                path = ""
                for i in range(row + 1):  # Generate the path based on the level
                    path += "/" + str(counter[i])

                # Find the description
                lines_after = self.lshw.split(line)[1].splitlines()
                description_line = lines_after[1].strip() if len(lines_after) > 1 else ''
                name = description_line.split(":")[1].strip() if ":" in description_line else description_line

                # Reset counters for deeper levels
                for i in range(row + 1, len(counter)):
                    counter[i] = 0

                item = [path, line.lstrip(), name]  # Include the path, line, and the extracted name
                items.append(item)

        # Debug: Print all items
        #print("Items:")
        #for item in items:
        #    print(f"Path: {item[0]}, Description: {item[1]}, Name: {item[2]}")

        # Populate the QTreeWidget
        self.build_tree_from_items(items)

            
    def build_tree_from_items(self, items):
        self.tree.clear()
        item_map = {}

        for path, description, name in items:
            path_parts = path.split('/')[1:]  # Remove the leading empty part
            current_item = self.tree.invisibleRootItem()
            parent_path = ""

            for part in path_parts:
                current_path = f"{parent_path}/{part}"
                if current_path not in item_map:
                    new_item = QTreeWidgetItem(current_item, [name])
                    new_item.setData(0, 1, description)  # Store the old description as data
                    item_map[current_path] = new_item
                current_item = item_map[current_path]
                parent_path = current_path
                
                
                # Expand the first two levels
                if len(path_parts) <= 2:
                    current_item.setExpanded(True)

    def on_item_clicked(self, item, column):
        data = item.data(0, 1)
        if data:
            
            # Extract the details for the selected item
            item_info_start = self.lshw.find(data)
            if item_info_start != -1:
                item_info_end = self.lshw.find("*-", item_info_start + len(data))
                item_info = self.lshw[item_info_start:item_info_end].strip() if item_info_end != -1 else self.lshw[item_info_start:].strip()

                item_info = item_info.split("\n",1)[1]
                # Combine item-specific info
                wrapped_item_info = self.wrap_text(item_info, 90)
                self.item_info_label.setText(wrapped_item_info)
            else:
                self.item_info_label.setText(f"Details not found for: {data}")
        else:
            self.item_info_label.setText("Select a hardware component to see details.")

    def wrap_text(self, text, width):
        wrapped_lines = []
        for line in text.splitlines():
            wrapped_lines.extend(textwrap.wrap(line.strip(), width=width))  # Remove leading/trailing spaces before wrapping
        return "\n".join(wrapped_lines)
        
    
    def set_basicinfo(self):
        # Extract the basic system info (before the first *-)
        basic_info = self.lshw.split("*-")[0].strip()
        basic_info = "\n".join(basic_info.splitlines()[1:6])
        if "lshwReport" in basic_info:
            workinfo = []
            for line in basic_info.splitlines():
                if "lshwReport" not in line:
                    workinfo.append(line)
            basic_info = "\n".join(workinfo)
        wrapped_basic_info = self.wrap_text(basic_info, 90)
        self.basic_info_label.setText(wrapped_basic_info)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LshwTreeWidget()
    window.show()
    sys.exit(app.exec_())
