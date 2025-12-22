import sys
import json
import struct
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                             QVBoxLayout, QWidget, QFileDialog, QMessageBox, 
                             QLabel, QHBoxLayout, QListWidget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBC Converter - Spell & Item Template to SQL")
        self.resize(900, 600)
        
        self.info_label = QLabel("Load a JSON file to convert (supports armory_spell and item_template)")
        self.text_edit = QTextEdit()
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        load_btn = QPushButton("Load JSON File")
        load_btn.clicked.connect(self.load_json)
        
        generate_btn = QPushButton("Generate and Save SQL")
        generate_btn.clicked.connect(self.generate_sql)
        
        validate_btn = QPushButton("Validate & Fix SQL Files")
        validate_btn.clicked.connect(self.validate_sql_files)
        
        button_layout.addWidget(load_btn)
        button_layout.addWidget(generate_btn)
        button_layout.addWidget(validate_btn)
        
        layout = QVBoxLayout()
        layout.addWidget(self.info_label)
        layout.addWidget(self.text_edit)
        layout.addLayout(button_layout)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_json(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'r', encoding='utf-8') as f:
                self.text_edit.setText(f.read())

    def generate_sql(self):
        try:
            data = json.loads(self.text_edit.toPlainText())
            table_name = data.get('table', '')
            rows = data.get('rows', [])
            
            if not rows:
                raise ValueError("No rows found in JSON")
            
            # Detect table type and convert accordingly
            if table_name == 'armory_spell':
                sql_content = [self.convert_spell_to_sql(row) for row in rows]
                default_filename = "spell_dbc.sql"
            elif table_name == 'item_template':
                sql_content = [self.convert_item_to_sql(row) for row in rows]
                default_filename = "item_dbc.sql"
            else:
                raise ValueError(f"Unknown table type: {table_name}. Supported: armory_spell, item_template")
            
            file_name, _ = QFileDialog.getSaveFileName(self, "Save SQL File", default_filename, "SQL Files (*.sql)")
            if file_name:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(sql_content))
                QMessageBox.information(self, "Success", f"SQL file saved to {file_name}\nConverted {len(sql_content)} rows from {table_name}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def validate_sql_files(self):
        """Open dialog to select and validate multiple SQL files"""
        file_names, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select SQL Files to Validate", 
            "", 
            "SQL Files (*.sql)"
        )
        
        if not file_names:
            return
        
        results = []
        fixed_files = []
        
        for file_path in file_names:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if it's a spell_dbc file
                if 'spell_dbc' in content.lower():
                    fixed_content, issues = self.validate_and_fix_spell_sql(content)
                    
                    if issues:
                        # Save the fixed version
                        backup_path = file_path + ".backup"
                        os.rename(file_path, backup_path)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(fixed_content)
                        
                        fixed_files.append(os.path.basename(file_path))
                        results.append(f"✓ Fixed: {os.path.basename(file_path)}\n  Issues: {', '.join(issues)}\n  Backup: {os.path.basename(backup_path)}")
                    else:
                        results.append(f"✓ Valid: {os.path.basename(file_path)} (no issues found)")
                else:
                    results.append(f"⚠ Skipped: {os.path.basename(file_path)} (not a spell_dbc file)")
                    
            except Exception as e:
                results.append(f"✗ Error: {os.path.basename(file_path)} - {str(e)}")
        
        # Show results
        result_text = "\n\n".join(results)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Validation Results")
        msg.setText(f"Validated {len(file_names)} file(s)\nFixed {len(fixed_files)} file(s)")
        msg.setDetailedText(result_text)
        msg.exec()

    def validate_and_fix_spell_sql(self, sql_content):
        """Validate and fix common issues in spell_dbc SQL"""
        issues = []
        
        # Split by INSERT statements (handle multi-line statements)
        statements = []
        current_statement = []
        
        for line in sql_content.split('\n'):
            if line.strip().startswith('INSERT'):
                if current_statement:
                    statements.append('\n'.join(current_statement))
                current_statement = [line]
            elif current_statement:
                current_statement.append(line)
            else:
                statements.append(line)
        
        if current_statement:
            statements.append('\n'.join(current_statement))
        
        fixed_statements = []
        
        for statement in statements:
            if not statement.strip() or not 'INSERT' in statement:
                fixed_statements.append(statement)
                continue
            
            # Join all lines into one for processing
            fixed_line = ' '.join(statement.split('\n'))
            # Join all lines into one for processing
            fixed_line = ' '.join(statement.split('\n'))
            
            # Fix 1: Clean up garbled language fields (non-English)
            lang_fields = [
                'Name_Lang_deDE', 'Name_Lang_frFR', 'Name_Lang_zhCN', 'Name_Lang_esES', 
                'Name_Lang_ruRU', 'Name_Lang_enCN', 'Name_Lang_enTW', 'Name_Lang_esMX',
                'Name_Lang_ptPT', 'Name_Lang_ptBR', 'Name_Lang_itIT', 'Name_Lang_enGB',
                'Name_Lang_koKR', 'Name_Lang_zhTW', 'Name_Lang_Unk',
                'NameSubtext_Lang_deDE', 'NameSubtext_Lang_frFR', 'NameSubtext_Lang_zhCN',
                'NameSubtext_Lang_esES', 'NameSubtext_Lang_ruRU', 'NameSubtext_Lang_enCN',
                'NameSubtext_Lang_enTW', 'NameSubtext_Lang_esMX', 'NameSubtext_Lang_ptPT',
                'NameSubtext_Lang_ptBR', 'NameSubtext_Lang_itIT', 'NameSubtext_Lang_enGB',
                'NameSubtext_Lang_koKR', 'NameSubtext_Lang_zhTW', 'NameSubtext_Lang_Unk',
                'Description_Lang_deDE', 'Description_Lang_frFR', 'Description_Lang_zhCN',
                'Description_Lang_esES', 'Description_Lang_ruRU', 'Description_Lang_enCN',
                'Description_Lang_enTW', 'Description_Lang_esMX', 'Description_Lang_ptPT',
                'Description_Lang_ptBR', 'Description_Lang_itIT', 'Description_Lang_enGB',
                'Description_Lang_koKR', 'Description_Lang_zhTW', 'Description_Lang_Unk',
                'AuraDescription_Lang_deDE', 'AuraDescription_Lang_frFR', 'AuraDescription_Lang_zhCN',
                'AuraDescription_Lang_esES', 'AuraDescription_Lang_ruRU', 'AuraDescription_Lang_enCN',
                'AuraDescription_Lang_enTW', 'AuraDescription_Lang_esMX', 'AuraDescription_Lang_ptPT',
                'AuraDescription_Lang_ptBR', 'AuraDescription_Lang_itIT', 'AuraDescription_Lang_enGB',
                'AuraDescription_Lang_koKR', 'AuraDescription_Lang_zhTW', 'AuraDescription_Lang_Unk'
            ]
            
            # Extract the SET clause and the fields
            if ' SET ' in fixed_line:
                parts = fixed_line.split(' SET ', 1)
                insert_part = parts[0] + ' SET '
                set_clause = parts[1].rstrip(';').strip()
                
                # Parse existing field assignments
                field_assignments = {}
                # Split by comma but not inside quotes
                current_field = ''
                in_quotes = False
                escape_next = False
                
                for char in set_clause:
                    if escape_next:
                        current_field += char
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        current_field += char
                        escape_next = True
                        continue
                        
                    if char == "'" and not escape_next:
                        in_quotes = not in_quotes
                        
                    if char == ',' and not in_quotes:
                        if '=' in current_field:
                            field_name = current_field.split('=')[0].strip().strip('`')
                            field_assignments[field_name] = current_field.strip()
                        current_field = ''
                    else:
                        current_field += char
                
                # Don't forget the last field
                if current_field and '=' in current_field:
                    field_name = current_field.split('=')[0].strip().strip('`')
                    field_assignments[field_name] = current_field.strip()
                
                # Fix garbled text in language fields
                for field in lang_fields:
                    if field in field_assignments:
                        assignment = field_assignments[field]
                        # Check if contains non-ASCII characters
                        if any(ord(c) > 127 for c in assignment):
                            field_assignments[field] = f"`{field}` = ''"
                            if 'garbled_text' not in issues:
                                issues.append('garbled_text')
                
                # Add missing language fields
                for field in lang_fields:
                    if field not in field_assignments:
                        field_assignments[field] = f"`{field}` = ''"
                        if 'missing_fields' not in issues:
                            issues.append('missing_fields')
                
                # Rebuild the SQL statement with proper formatting
                fixed_line = insert_part + ', \n'.join(field_assignments.values()) + ';'
            
            fixed_statements.append(fixed_line)
        
        return '\n\n'.join(fixed_statements), issues

    def _is_clean_ascii(self, text):
        """Check if text is clean ASCII or has garbled encoding"""
        if not text:
            return True
        # If it contains lots of special UTF-8 chars, it's probably garbled
        special_count = sum(1 for c in text if ord(c) > 127)
        return special_count < len(text) * 0.3  # Less than 30% special chars

    def convert_item_to_sql(self, row):
        """Convert item_template JSON to item_dbc SQL"""
        mapping = {
            'entry': 'ID',
            'class': 'ClassID',
            'subclass': 'SubclassID',
            'SoundOverrideSubclass': 'Sound_Override_Subclassid',
            'Material': 'Material',
            'displayid': 'DisplayInfoID',
            'InventoryType': 'InventoryType',
            'sheath': 'SheatheType'
        }
        
        values = []
        for json_key, dbc_col in mapping.items():
            if json_key in row:
                values.append(str(int(row[json_key])))
            else:
                values.append('0')
        
        columns = ', '.join(f'`{col}`' for col in mapping.values())
        values_str = ', '.join(values)
        
        return f"INSERT INTO `item_dbc` ({columns}) VALUES ({values_str});"

    def convert_spell_to_sql(self, row):
        """Convert armory_spell JSON to spell_dbc SQL"""
        mapping = {
            'id': ('ID', 'int'),
            'Category': ('Category', 'int'),
            'Dispel': ('DispelType', 'int'),
            'Mechanic': ('Mechanic', 'int'),
            'Attributes': ('Attributes', 'int'),
            'AttributesEx': ('AttributesEx', 'int'),
            'AttributesEx2': ('AttributesEx2', 'int'),
            'AttributesEx3': ('AttributesEx3', 'int'),
            'AttributesEx4': ('AttributesEx4', 'int'),
            'AttributesEx5': ('AttributesEx5', 'int'),
            'AttributesEx6': ('AttributesEx6', 'int'),
            'unk_320_1': ('AttributesEx7', 'int'),
            'Stances': ('ShapeshiftMask', 'int'),
            'unk_320_2': ('unk_320_2', 'int'),
            'StancesNot': ('ShapeshiftExclude', 'int'),
            'unk_320_3': ('unk_320_3', 'int'),
            'Targets': ('Targets', 'int'),
            'TargetCreatureType': ('TargetCreatureType', 'int'),
            'RequiresSpellFocus': ('RequiresSpellFocus', 'int'),
            'FacingCasterFlags': ('FacingCasterFlags', 'int'),
            'CasterAuraState': ('CasterAuraState', 'int'),
            'TargetAuraState': ('TargetAuraState', 'int'),
            'CasterAuraStateNot': ('ExcludeCasterAuraState', 'int'),
            'TargetAuraStateNot': ('ExcludeTargetAuraState', 'int'),
            'casterAuraSpell': ('CasterAuraSpell', 'int'),
            'targetAuraSpell': ('TargetAuraSpell', 'int'),
            'excludeCasterAuraSpell': ('ExcludeCasterAuraSpell', 'int'),
            'excludeTargetAuraSpell': ('ExcludeTargetAuraSpell', 'int'),
            'CastingTimeIndex': ('CastingTimeIndex', 'int'),
            'RecoveryTime': ('RecoveryTime', 'int'),
            'CategoryRecoveryTime': ('CategoryRecoveryTime', 'int'),
            'InterruptFlags': ('InterruptFlags', 'int'),
            'AuraInterruptFlags': ('AuraInterruptFlags', 'int'),
            'ChannelInterruptFlags': ('ChannelInterruptFlags', 'int'),
            'procFlags': ('ProcTypeMask', 'int'),
            'procChance': ('ProcChance', 'int'),
            'procCharges': ('ProcCharges', 'int'),
            'maxLevel': ('MaxLevel', 'int'),
            'baseLevel': ('BaseLevel', 'int'),
            'spellLevel': ('SpellLevel', 'int'),
            'DurationIndex': ('DurationIndex', 'int'),
            'powerType': ('PowerType', 'int'),
            'manaCost': ('ManaCost', 'int'),
            'manaCostPerlevel': ('ManaCostPerLevel', 'int'),
            'manaPerSecond': ('ManaPerSecond', 'int'),
            'manaPerSecondPerLevel': ('ManaPerSecondPerLevel', 'int'),
            'rangeIndex': ('RangeIndex', 'int'),
            'speed': ('Speed', 'float'),
            'modalNextSpell': ('ModalNextSpell', 'int'),
            'StackAmount': ('CumulativeAura', 'int'),
            'Totem_1': ('Totem_1', 'int'),
            'Totem_2': ('Totem_2', 'int'),
            'Reagent_1': ('Reagent_1', 'int'),
            'Reagent_2': ('Reagent_2', 'int'),
            'Reagent_3': ('Reagent_3', 'int'),
            'Reagent_4': ('Reagent_4', 'int'),
            'Reagent_5': ('Reagent_5', 'int'),
            'Reagent_6': ('Reagent_6', 'int'),
            'Reagent_7': ('Reagent_7', 'int'),
            'Reagent_8': ('Reagent_8', 'int'),
            'ReagentCount_1': ('ReagentCount_1', 'int'),
            'ReagentCount_2': ('ReagentCount_2', 'int'),
            'ReagentCount_3': ('ReagentCount_3', 'int'),
            'ReagentCount_4': ('ReagentCount_4', 'int'),
            'ReagentCount_5': ('ReagentCount_5', 'int'),
            'ReagentCount_6': ('ReagentCount_6', 'int'),
            'ReagentCount_7': ('ReagentCount_7', 'int'),
            'ReagentCount_8': ('ReagentCount_8', 'int'),
            'EquippedItemClass': ('EquippedItemClass', 'int'),
            'EquippedItemSubClassMask': ('EquippedItemSubclass', 'int'),
            'EquippedItemInventoryTypeMask': ('EquippedItemInvTypes', 'int'),
            'Effect_1': ('Effect_1', 'int'),
            'Effect_2': ('Effect_2', 'int'),
            'Effect_3': ('Effect_3', 'int'),
            'EffectDieSides_1': ('EffectDieSides_1', 'int'),
            'EffectDieSides_2': ('EffectDieSides_2', 'int'),
            'EffectDieSides_3': ('EffectDieSides_3', 'int'),
            'EffectRealPointsPerLevel_1': ('EffectRealPointsPerLevel_1', 'float'),
            'EffectRealPointsPerLevel_2': ('EffectRealPointsPerLevel_2', 'float'),
            'EffectRealPointsPerLevel_3': ('EffectRealPointsPerLevel_3', 'float'),
            'EffectBasePoints_1': ('EffectBasePoints_1', 'int'),
            'EffectBasePoints_2': ('EffectBasePoints_2', 'int'),
            'EffectBasePoints_3': ('EffectBasePoints_3', 'int'),
            'EffectMechanic_1': ('EffectMechanic_1', 'int'),
            'EffectMechanic_2': ('EffectMechanic_2', 'int'),
            'EffectMechanic_3': ('EffectMechanic_3', 'int'),
            'EffectImplicitTargetA_1': ('ImplicitTargetA_1', 'int'),
            'EffectImplicitTargetA_2': ('ImplicitTargetA_2', 'int'),
            'EffectImplicitTargetA_3': ('ImplicitTargetA_3', 'int'),
            'EffectImplicitTargetB_1': ('ImplicitTargetB_1', 'int'),
            'EffectImplicitTargetB_2': ('ImplicitTargetB_2', 'int'),
            'EffectImplicitTargetB_3': ('ImplicitTargetB_3', 'int'),
            'EffectRadiusIndex_1': ('EffectRadiusIndex_1', 'int'),
            'EffectRadiusIndex_2': ('EffectRadiusIndex_2', 'int'),
            'EffectRadiusIndex_3': ('EffectRadiusIndex_3', 'int'),
            'EffectApplyAuraName_1': ('EffectAura_1', 'int'),
            'EffectApplyAuraName_2': ('EffectAura_2', 'int'),
            'EffectApplyAuraName_3': ('EffectAura_3', 'int'),
            'EffectAmplitude_1': ('EffectAuraPeriod_1', 'int'),
            'EffectAmplitude_2': ('EffectAuraPeriod_2', 'int'),
            'EffectAmplitude_3': ('EffectAuraPeriod_3', 'int'),
            'EffectMultipleValue_1': ('EffectMultipleValue_1', 'float'),
            'EffectMultipleValue_2': ('EffectMultipleValue_2', 'float'),
            'EffectMultipleValue_3': ('EffectMultipleValue_3', 'float'),
            'EffectChainTarget_1': ('EffectChainTargets_1', 'int'),
            'EffectChainTarget_2': ('EffectChainTargets_2', 'int'),
            'EffectChainTarget_3': ('EffectChainTargets_3', 'int'),
            'EffectItemType_1': ('EffectItemType_1', 'int'),
            'EffectItemType_2': ('EffectItemType_2', 'int'),
            'EffectItemType_3': ('EffectItemType_3', 'int'),
            'EffectMiscValue_1': ('EffectMiscValue_1', 'int'),
            'EffectMiscValue_2': ('EffectMiscValue_2', 'int'),
            'EffectMiscValue_3': ('EffectMiscValue_3', 'int'),
            'EffectMiscValueB_1': ('EffectMiscValueB_1', 'int'),
            'EffectMiscValueB_2': ('EffectMiscValueB_2', 'int'),
            'EffectMiscValueB_3': ('EffectMiscValueB_3', 'int'),
            'EffectTriggerSpell_1': ('EffectTriggerSpell_1', 'int'),
            'EffectTriggerSpell_2': ('EffectTriggerSpell_2', 'int'),
            'EffectTriggerSpell_3': ('EffectTriggerSpell_3', 'int'),
            'EffectPointsPerComboPoint_1': ('EffectPointsPerCombo_1', 'float'),
            'EffectPointsPerComboPoint_2': ('EffectPointsPerCombo_2', 'float'),
            'EffectPointsPerComboPoint_3': ('EffectPointsPerCombo_3', 'float'),
            'EffectSpellClassMaskA_1': ('EffectSpellClassMaskA_1', 'int'),
            'EffectSpellClassMaskA_2': ('EffectSpellClassMaskA_2', 'int'),
            'EffectSpellClassMaskA_3': ('EffectSpellClassMaskA_3', 'int'),
            'EffectSpellClassMaskB_1': ('EffectSpellClassMaskB_1', 'int'),
            'EffectSpellClassMaskB_2': ('EffectSpellClassMaskB_2', 'int'),
            'EffectSpellClassMaskB_3': ('EffectSpellClassMaskB_3', 'int'),
            'EffectSpellClassMaskC_1': ('EffectSpellClassMaskC_1', 'int'),
            'EffectSpellClassMaskC_2': ('EffectSpellClassMaskC_2', 'int'),
            'EffectSpellClassMaskC_3': ('EffectSpellClassMaskC_3', 'int'),
            'SpellVisual_1': ('SpellVisualID_1', 'int'),
            'SpellVisual_2': ('SpellVisualID_2', 'int'),
            'SpellIconID': ('SpellIconID', 'int'),
            'activeIconID': ('ActiveIconID', 'int'),
            'spellPriority': ('SpellPriority', 'int'),
            'SpellName_en_gb': ('Name_Lang_enUS', 'str'),
            'SpellNameFlag': ('Name_Lang_Mask', 'int'),
            'RankFlags': ('NameSubtext_Lang_Mask', 'int'),
            'Description_en_gb': ('Description_Lang_enUS', 'str'),
            'DescriptionFlags': ('Description_Lang_Mask', 'int'),
            'ToolTip_1': ('AuraDescription_Lang_enUS', 'str'),
            'ToolTipFlags': ('AuraDescription_Lang_Mask', 'int'),
            'ManaCostPercentage': ('ManaCostPct', 'int'),
            'StartRecoveryCategory': ('StartRecoveryCategory', 'int'),
            'StartRecoveryTime': ('StartRecoveryTime', 'int'),
            'MaxTargetLevel': ('MaxTargetLevel', 'int'),
            'SpellFamilyName': ('SpellClassSet', 'int'),
            'SpellFamilyFlags': ('SpellClassMask_1', 'int'),
            'SpellFamilyFlags2': ('SpellClassMask_2', 'int'),
            'MaxAffectedTargets': ('MaxTargets', 'int'),
            'DmgClass': ('DefenseType', 'int'),
            'PreventionType': ('PreventionType', 'int'),
            'StanceBarOrder': ('StanceBarOrder', 'int'),
            'DmgMultiplier_1': ('EffectChainAmplitude_1', 'float'),
            'DmgMultiplier_2': ('EffectChainAmplitude_2', 'float'),
            'DmgMultiplier_3': ('EffectChainAmplitude_3', 'float'),
            'MinFactionId': ('MinFactionID', 'int'),
            'MinReputation': ('MinReputation', 'int'),
            'RequiredAuraVision': ('RequiredAuraVision', 'int'),
            'TotemCategory_1': ('RequiredTotemCategoryID_1', 'int'),
            'TotemCategory_2': ('RequiredTotemCategoryID_2', 'int'),
            'AreaGroupId': ('RequiredAreasID', 'int'),
            'SchoolMask': ('SchoolMask', 'int'),
            'runeCostID': ('RuneCostID', 'int'),
            'spellMissileID': ('SpellMissileID', 'int'),
            'PowerDisplayId': ('PowerDisplayID', 'int'),
            'unk_320_4_1': ('EffectBonusMultiplier_1', 'float'),
            'unk_320_4_2': ('EffectBonusMultiplier_2', 'float'),
            'unk_320_4_3': ('EffectBonusMultiplier_3', 'float'),
            'spellDescriptionVariableID': ('SpellDescriptionVariableID', 'int'),
            'SpellDifficultyId': ('SpellDifficultyID', 'int'),
        }

        sql_parts = []
        for json_key, (dbc_col, type_hint) in mapping.items():
            if json_key in row:
                value = row[json_key]
                if type_hint == 'int':
                    value_str = str(int(value))
                elif type_hint == 'float':
                    if isinstance(value, int):
                        # Handle packed float (e.g., 1065353216 -> 1.0)
                        if value > 1000000 or (value >= 0 and value not in range(-100, 100)):
                            try:
                                value = struct.unpack('f', struct.pack('I', value))[0]
                            except struct.error:
                                value = float(value)
                        else:
                            value = float(value)
                    else:
                        value = float(value)
                    value_str = f"{value:.6f}" if value != int(value) else str(int(value))
                elif type_hint == 'str':
                    # Only keep clean English text, empty everything else
                    if self._is_clean_ascii(value):
                        value_str = "'" + value.replace("'", "\\'").replace('\\', '\\\\') + "'"
                    else:
                        value_str = "''"
                sql_parts.append(f"`{dbc_col}` = {value_str}")

        # Set default for SpellClassMask_3 if not present
        if 'SpellClassMask_3' not in [p.split('=')[0].strip(' `') for p in sql_parts]:
            sql_parts.append("`SpellClassMask_3` = 0")

        # Set all other language fields to '' (NOT from JSON data)
        all_lang_cols = [
            'Name_Lang_enGB', 'Name_Lang_koKR', 'Name_Lang_frFR', 'Name_Lang_deDE', 'Name_Lang_enCN', 'Name_Lang_zhCN',
            'Name_Lang_enTW', 'Name_Lang_zhTW', 'Name_Lang_esES', 'Name_Lang_esMX', 'Name_Lang_ruRU', 'Name_Lang_ptPT',
            'Name_Lang_ptBR', 'Name_Lang_itIT', 'Name_Lang_Unk',
            'NameSubtext_Lang_enUS', 'NameSubtext_Lang_enGB', 'NameSubtext_Lang_koKR', 'NameSubtext_Lang_frFR', 'NameSubtext_Lang_deDE', 'NameSubtext_Lang_enCN', 'NameSubtext_Lang_zhCN',
            'NameSubtext_Lang_enTW', 'NameSubtext_Lang_zhTW', 'NameSubtext_Lang_esES', 'NameSubtext_Lang_esMX', 'NameSubtext_Lang_ruRU', 'NameSubtext_Lang_ptPT',
            'NameSubtext_Lang_ptBR', 'NameSubtext_Lang_itIT', 'NameSubtext_Lang_Unk',
            'Description_Lang_enGB', 'Description_Lang_koKR', 'Description_Lang_frFR', 'Description_Lang_deDE', 'Description_Lang_enCN', 'Description_Lang_zhCN',
            'Description_Lang_enTW', 'Description_Lang_zhTW', 'Description_Lang_esES', 'Description_Lang_esMX', 'Description_Lang_ruRU', 'Description_Lang_ptPT',
            'Description_Lang_ptBR', 'Description_Lang_itIT', 'Description_Lang_Unk',
            'AuraDescription_Lang_enGB', 'AuraDescription_Lang_koKR', 'AuraDescription_Lang_frFR', 'AuraDescription_Lang_deDE', 'AuraDescription_Lang_enCN', 'AuraDescription_Lang_zhCN',
            'AuraDescription_Lang_enTW', 'AuraDescription_Lang_zhTW', 'AuraDescription_Lang_esES', 'AuraDescription_Lang_esMX', 'AuraDescription_Lang_ruRU', 'AuraDescription_Lang_ptPT',
            'AuraDescription_Lang_ptBR', 'AuraDescription_Lang_itIT', 'AuraDescription_Lang_Unk',
        ]
        set_cols = [p.split('=')[0].strip(' `') for p in sql_parts]
        for col in all_lang_cols:
            if col not in set_cols:
                sql_parts.append(f"`{col}` = ''")

        return "INSERT INTO `spell_dbc` SET \n" + ", \n".join(sql_parts) + ";"

    def _is_clean_ascii(self, text):
        """Check if text is clean ASCII/UTF-8 or has garbled encoding"""
        if not text:
            return True
        # If it contains lots of special UTF-8 chars like Ãƒ, it's probably garbled
        if 'Ãƒ' in text or 'Ã‚' in text:
            return False
        special_count = sum(1 for c in text if ord(c) > 127)
        return special_count < len(text) * 0.2  # Less than 20% special chars

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
