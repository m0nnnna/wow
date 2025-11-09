import sys
import json
import struct
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Armory Spell JSON to Spell DBC SQL Converter")
        self.text_edit = QTextEdit()
        load_btn = QPushButton("Load JSON File")
        load_btn.clicked.connect(self.load_json)
        generate_btn = QPushButton("Generate and Save SQL")
        generate_btn.clicked.connect(self.generate_sql)
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(load_btn)
        layout.addWidget(generate_btn)
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
            rows = data.get('rows', [])
            if not rows:
                raise ValueError("No rows found in JSON")
            sql_content = []
            for row in rows:
                sql = self.convert_to_sql(row)
                sql_content.append(sql)
            file_name, _ = QFileDialog.getSaveFileName(self, "Save SQL File", "", "SQL Files (*.sql)")
            if file_name:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(sql_content))
                QMessageBox.information(self, "Success", f"SQL file saved to {file_name}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _fix_mojibake(self, value):
        """Detect mojibake and set to empty string if unfixable; otherwise attempt fix."""
        if not isinstance(value, str) or not value.strip() or 'Ã' not in value:
            return value  # Empty or clean ASCII stays as-is
        
        # Quick check: if it's likely garbled (non-ASCII without valid UTF-8 feel), set to ""
        if any(ord(c) > 127 for c in value) and len(value) > 20:  # Heuristic for suspicious length
            print(f"Detected likely garbled string (len {len(value)}), setting to empty: {value[:30]}...")
            return ""
        
        # Attempt robust fix: build bytes from latin-1 range, decode with replace
        bytes_list = [ord(c) for c in value if ord(c) <= 255]
        try:
            fixed_bytes = bytes(bytes_list)
            fixed = fixed_bytes.decode('utf-8', errors='replace')
            # If fix introduces too many � (e.g., >5% of chars), treat as unfixable
            replacement_count = fixed.count('�')
            if replacement_count > len(fixed) * 0.05:
                print(f"Fix introduced too many � ({replacement_count}/{len(fixed)}), setting to empty")
                return ""
            orig_len = len(value)
            new_len = len(fixed)
            if new_len < orig_len:
                print(f"Fixed mojibake: original len {orig_len} -> fixed len {new_len}")
            return fixed
        except Exception as e:
            print(f"Fix failed ({e}), setting to empty for: {value[:30]}...")
            return ""

    def convert_to_sql(self, row):
        # Mapping: JSON key -> (DBC column, type_hint)
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
            'SpellName_de_de': ('Name_Lang_deDE', 'str'),
            'SpellName_fr_fr': ('Name_Lang_frFR', 'str'),
            'SpellName_zh_cn': ('Name_Lang_zhCN', 'str'),
            'SpellName_es_es': ('Name_Lang_esES', 'str'),
            'SpellName_ru_ru': ('Name_Lang_ruRU', 'str'),
            # Add more if needed for numbered
            'SpellName_5': ('Name_Lang_enCN', 'str'),
            'SpellName_6': ('Name_Lang_enTW', 'str'),
            'SpellName_8': ('Name_Lang_esMX', 'str'),
            'SpellName_10': ('Name_Lang_ptPT', 'str'),
            'SpellName_11': ('Name_Lang_ptBR', 'str'),
            'SpellName_12': ('Name_Lang_itIT', 'str'),
            'SpellNameFlag': ('Name_Lang_Mask', 'int'),
            'Rank_1': ('NameSubtext_Lang_enUS', 'str'),
            'Rank_2': ('NameSubtext_Lang_enGB', 'str'),
            'Rank_fr_fr': ('NameSubtext_Lang_frFR', 'str'),
            'Rank_zh_cn': ('NameSubtext_Lang_zhCN', 'str'),
            'Rank_es_es': ('NameSubtext_Lang_esES', 'str'),
            'Rank_ru_ru': ('NameSubtext_Lang_ruRU', 'str'),
            'Rank_5': ('NameSubtext_Lang_enCN', 'str'),
            'Rank_6': ('NameSubtext_Lang_enTW', 'str'),
            'Rank_8': ('NameSubtext_Lang_esMX', 'str'),
            'Rank_10': ('NameSubtext_Lang_ptPT', 'str'),
            'Rank_11': ('NameSubtext_Lang_ptBR', 'str'),
            'Rank_12': ('NameSubtext_Lang_itIT', 'str'),
            'RankFlags': ('NameSubtext_Lang_Mask', 'int'),
            'Description_en_gb': ('Description_Lang_enUS', 'str'),
            'Description_de_de': ('Description_Lang_deDE', 'str'),
            'Description_fr_fr': ('Description_Lang_frFR', 'str'),
            'Description_zh_cn': ('Description_Lang_zhCN', 'str'),
            'Description_es_es': ('Description_Lang_esES', 'str'),
            'Description_ru_ru': ('Description_Lang_ruRU', 'str'),
            'Description_5': ('Description_Lang_enCN', 'str'),
            'Description_6': ('Description_Lang_enTW', 'str'),
            'Description_8': ('Description_Lang_esMX', 'str'),
            'Description_10': ('Description_Lang_ptPT', 'str'),
            'Description_11': ('Description_Lang_ptBR', 'str'),
            'Description_12': ('Description_Lang_itIT', 'str'),
            'DescriptionFlags': ('Description_Lang_Mask', 'int'),
            'ToolTip_1': ('AuraDescription_Lang_enUS', 'str'),
            'ToolTip_de_de': ('AuraDescription_Lang_deDE', 'str'),
            'Tooltip_fr_fr': ('AuraDescription_Lang_frFR', 'str'),
            'Tooltip_zh_cn': ('AuraDescription_Lang_zhCN', 'str'),
            'Tooltip_es_es': ('AuraDescription_Lang_esES', 'str'),
            'Tooltip_ru_ru': ('AuraDescription_Lang_ruRU', 'str'),
            'ToolTip_5': ('AuraDescription_Lang_enCN', 'str'),
            'ToolTip_6': ('AuraDescription_Lang_enTW', 'str'),
            'ToolTip_8': ('AuraDescription_Lang_esMX', 'str'),
            'ToolTip_10': ('AuraDescription_Lang_ptPT', 'str'),
            'ToolTip_11': ('AuraDescription_Lang_ptBR', 'str'),
            'ToolTip_12': ('AuraDescription_Lang_itIT', 'str'),
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
                        value = struct.unpack('f', struct.pack('I', value))[0]
                    else:
                        value = float(value)
                    value_str = f"{value:.6f}" if value != int(value) else str(int(value))
                elif type_hint == 'str':
                    # Scan and clean garbled strings before escaping
                    value = self._fix_mojibake(value)
                    value_str = "'" + value.replace("'", "\\'").replace('\\', '\\\\') + "'"
                sql_parts.append(f"`{dbc_col}` = {value_str}")

        # Set default for SpellClassMask_3 if not present
        if 'SpellClassMask_3' not in [p.split('=')[0].strip(' `') for p in sql_parts]:
            sql_parts.append("`SpellClassMask_3` = 0")

        # Set all other language fields to ''
        all_lang_cols = [
            'Name_Lang_enGB', 'Name_Lang_koKR', 'Name_Lang_frFR', 'Name_Lang_deDE', 'Name_Lang_enCN', 'Name_Lang_zhCN',
            'Name_Lang_enTW', 'Name_Lang_zhTW', 'Name_Lang_esES', 'Name_Lang_esMX', 'Name_Lang_ruRU', 'Name_Lang_ptPT',
            'Name_Lang_ptBR', 'Name_Lang_itIT', 'Name_Lang_Unk',
            'NameSubtext_Lang_enGB', 'NameSubtext_Lang_koKR', 'NameSubtext_Lang_frFR', 'NameSubtext_Lang_deDE', 'NameSubtext_Lang_enCN', 'NameSubtext_Lang_zhCN',
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

        return "INSERT INTO `spell_dbc` SET " + ", \n".join(sql_parts) + ";"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())