"""
ISO 22000:2018 Compliant Stage Templates for Production Processes

This module provides predefined stage templates that comply with ISO 22000:2018 requirements
for food safety management systems. These templates include Critical Control Points (CCPs)
and Operational Prerequisite Programs (OPRPs) as required by the standard.

References:
- ISO 22000:2018 Food safety management systems
- ISO/TS 22002-1:2009 Prerequisite programmes on food safety
- HACCP Principles and Application Guidelines
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta


class ISO22000StageTemplates:
    """ISO 22000:2018 compliant stage templates for various product types"""
    
    @staticmethod
    def get_fresh_milk_stages() -> List[Dict[str, Any]]:
        """
        Fresh milk processing stages compliant with ISO 22000:2018
        
        Key Critical Control Points:
        - Pasteurization temperature and time (CCP)
        - Rapid cooling (OPRP)
        - Cold storage temperature (OPRP)
        """
        return [
            {
                "stage_name": "Raw Milk Reception",
                "stage_description": "Reception and initial quality control of raw milk",
                "sequence_order": 1,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 30,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "minimum_duration_minutes": 15
                },
                "stage_notes": "Check temperature, pH, and visual inspection. ISO 22000:2018 Clause 7.4.2"
            },
            {
                "stage_name": "Filtration and Clarification",
                "stage_description": "Remove physical contaminants and debris",
                "sequence_order": 2,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 20,
                "completion_criteria": {
                    "mandatory_monitoring_required": True
                },
                "stage_notes": "Ensure proper filtration to remove foreign matter. ISO 22000:2018 Clause 7.4.3"
            },
            {
                "stage_name": "HTST Pasteurization",
                "stage_description": "High Temperature Short Time pasteurization - CRITICAL CONTROL POINT",
                "sequence_order": 3,
                "is_critical_control_point": True,
                "is_operational_prp": False,
                "duration_minutes": 45,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "minimum_duration_minutes": 30,
                    "temperature_verification_required": True
                },
                "stage_notes": "Critical Control Point: 72°C for 15 seconds minimum. ISO 22000:2018 Clause 8.5.4"
            },
            {
                "stage_name": "Rapid Cooling",
                "stage_description": "Cool milk rapidly to prevent bacterial growth",
                "sequence_order": 4,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 20,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "maximum_temperature_4c": True
                },
                "stage_notes": "Cool to ≤4°C within 20 minutes. OPRP requirement. ISO 22000:2018 Clause 8.5.3"
            },
            {
                "stage_name": "Packaging",
                "stage_description": "Aseptic packaging in sterile containers",
                "sequence_order": 5,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 30,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "container_integrity_check": True
                },
                "stage_notes": "Ensure sterile packaging environment. ISO 22000:2018 Clause 7.4.4"
            },
            {
                "stage_name": "Cold Storage",
                "stage_description": "Store finished product under refrigeration",
                "sequence_order": 6,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 15,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "storage_temperature_verification": True
                },
                "stage_notes": "Maintain ≤4°C storage temperature. ISO 22000:2018 Clause 8.5.1"
            }
        ]
    
    @staticmethod
    def get_yoghurt_stages() -> List[Dict[str, Any]]:
        """
        Yoghurt processing stages compliant with ISO 22000:2018
        
        Key Critical Control Points:
        - Pasteurization (CCP)
        - Fermentation temperature and pH (CCP)
        - Cold storage (OPRP)
        """
        return [
            {
                "stage_name": "Milk Reception and Standardization",
                "stage_description": "Receive milk and adjust fat content",
                "sequence_order": 1,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 45,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "fat_content_verification": True
                },
                "stage_notes": "Standardize fat content to 3.25%. Check incoming milk quality. ISO 22000:2018 Clause 7.4.2"
            },
            {
                "stage_name": "Homogenization",
                "stage_description": "Break down fat globules for uniform texture",
                "sequence_order": 2,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 30,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "pressure_verification": True
                },
                "stage_notes": "Operate at 2000-2500 psi. Monitor pressure and temperature. ISO 22000:2018 Clause 7.4.3"
            },
            {
                "stage_name": "Pasteurization",
                "stage_description": "Heat treatment to eliminate pathogens - CRITICAL CONTROL POINT",
                "sequence_order": 3,
                "is_critical_control_point": True,
                "is_operational_prp": False,
                "duration_minutes": 60,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "minimum_duration_minutes": 45,
                    "temperature_time_verification": True
                },
                "stage_notes": "CCP: 85°C for 30 minutes or 95°C for 5 minutes. ISO 22000:2018 Clause 8.5.4"
            },
            {
                "stage_name": "Cooling for Inoculation",
                "stage_description": "Cool to optimal temperature for culture addition",
                "sequence_order": 4,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 25,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "target_temperature_43c": True
                },
                "stage_notes": "Cool to 43°C ± 2°C for optimal culture activity. ISO 22000:2018 Clause 8.5.3"
            },
            {
                "stage_name": "Culture Inoculation",
                "stage_description": "Add starter cultures for fermentation",
                "sequence_order": 5,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 15,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "culture_viability_check": True
                },
                "stage_notes": "Add 2-3% starter culture. Verify culture viability. ISO 22000:2018 Clause 7.4.4"
            },
            {
                "stage_name": "Fermentation",
                "stage_description": "Controlled fermentation to develop acidity - CRITICAL CONTROL POINT",
                "sequence_order": 6,
                "is_critical_control_point": True,
                "is_operational_prp": False,
                "duration_minutes": 240,  # 4 hours
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "ph_target_4_5": True,
                    "minimum_duration_minutes": 180
                },
                "stage_notes": "CCP: Maintain 43°C, target pH 4.5. Monitor every 30 minutes. ISO 22000:2018 Clause 8.5.4"
            },
            {
                "stage_name": "Cooling and Packaging",
                "stage_description": "Cool product and package in sterile containers",
                "sequence_order": 7,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 45,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "final_temperature_4c": True
                },
                "stage_notes": "Cool to 4°C and package aseptically. ISO 22000:2018 Clause 7.4.4"
            },
            {
                "stage_name": "Cold Storage",
                "stage_description": "Store finished yoghurt under refrigeration",
                "sequence_order": 8,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 15,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "storage_temperature_verification": True
                },
                "stage_notes": "Maintain ≤4°C. Monitor continuously. ISO 22000:2018 Clause 8.5.1"
            }
        ]
    
    @staticmethod
    def get_cheese_stages() -> List[Dict[str, Any]]:
        """
        Cheese processing stages compliant with ISO 22000:2018
        
        Key Critical Control Points:
        - Pasteurization (CCP)
        - pH control during acidification (CCP)
        - Aging temperature and humidity (OPRP)
        """
        return [
            {
                "stage_name": "Milk Reception and Testing",
                "stage_description": "Receive and test raw milk quality",
                "sequence_order": 1,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 60,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "quality_tests_complete": True
                },
                "stage_notes": "Test for antibiotics, somatic cells, bacterial count. ISO 22000:2018 Clause 7.4.2"
            },
            {
                "stage_name": "Pasteurization",
                "stage_description": "Heat treatment for pathogen elimination - CRITICAL CONTROL POINT",
                "sequence_order": 2,
                "is_critical_control_point": True,
                "is_operational_prp": False,
                "duration_minutes": 45,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "temperature_time_verification": True,
                    "minimum_duration_minutes": 30
                },
                "stage_notes": "CCP: 72°C for 15 seconds or equivalent. Continuous monitoring. ISO 22000:2018 Clause 8.5.4"
            },
            {
                "stage_name": "Cooling and Culture Addition",
                "stage_description": "Cool milk and add starter cultures",
                "sequence_order": 3,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 30,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "temperature_32c": True
                },
                "stage_notes": "Cool to 32°C, add mesophilic cultures. ISO 22000:2018 Clause 7.4.4"
            },
            {
                "stage_name": "Acidification",
                "stage_description": "Develop acidity through bacterial fermentation - CRITICAL CONTROL POINT",
                "sequence_order": 4,
                "is_critical_control_point": True,
                "is_operational_prp": False,
                "duration_minutes": 90,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "ph_monitoring_required": True,
                    "minimum_duration_minutes": 60
                },
                "stage_notes": "CCP: Monitor pH every 15 minutes. Target pH 6.3-6.4 before renneting. ISO 22000:2018 Clause 8.5.4"
            },
            {
                "stage_name": "Renneting and Coagulation",
                "stage_description": "Add rennet and form curd",
                "sequence_order": 5,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 45,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "curd_firmness_check": True
                },
                "stage_notes": "Add rennet, maintain 32°C. Check curd firmness. ISO 22000:2018 Clause 7.4.3"
            },
            {
                "stage_name": "Cutting and Draining",
                "stage_description": "Cut curd and drain whey",
                "sequence_order": 6,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 120,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "moisture_content_check": True
                },
                "stage_notes": "Cut curd uniformly, control drainage rate. ISO 22000:2018 Clause 7.4.3"
            },
            {
                "stage_name": "Pressing",
                "stage_description": "Press curd to remove additional whey",
                "sequence_order": 7,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 360,  # 6 hours
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "pressure_gradient_applied": True
                },
                "stage_notes": "Apply graduated pressure. Monitor for 6 hours. ISO 22000:2018 Clause 7.4.3"
            },
            {
                "stage_name": "Salting",
                "stage_description": "Apply salt for preservation and flavor",
                "sequence_order": 8,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 30,
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "salt_concentration_check": True
                },
                "stage_notes": "Dry salting or brine application. Monitor salt penetration. ISO 22000:2018 Clause 7.4.4"
            },
            {
                "stage_name": "Aging/Ripening",
                "stage_description": "Controlled aging for flavor and texture development",
                "sequence_order": 9,
                "is_critical_control_point": False,
                "is_operational_prp": True,
                "duration_minutes": 43200,  # 30 days (example)
                "completion_criteria": {
                    "mandatory_monitoring_required": True,
                    "temperature_humidity_control": True
                },
                "stage_notes": "OPRP: Maintain 10-15°C, 85% RH. Daily monitoring. ISO 22000:2018 Clause 8.5.3"
            }
        ]
    
    @staticmethod
    def get_monitoring_requirements_for_stage(stage_name: str, is_ccp: bool = False) -> List[Dict[str, Any]]:
        """
        Get ISO 22000:2018 compliant monitoring requirements for specific stages
        
        Args:
            stage_name: Name of the stage
            is_ccp: Whether the stage is a Critical Control Point
            
        Returns:
            List of monitoring requirement dictionaries
        """
        
        # Common monitoring requirements based on stage type
        common_requirements = {
            "pasteurization": [
                {
                    "requirement_name": "Temperature Monitoring",
                    "requirement_type": "temperature",
                    "description": "Continuous temperature monitoring during pasteurization",
                    "is_critical_limit": True,
                    "target_value": 72.0,
                    "tolerance_min": 71.5,
                    "tolerance_max": 75.0,
                    "unit_of_measure": "°C",
                    "monitoring_frequency": "continuous",
                    "is_mandatory": True,
                    "equipment_required": "Calibrated thermometer",
                    "measurement_method": "Electronic temperature probe",
                    "calibration_required": True,
                    "regulatory_reference": "ISO 22000:2018 Clause 8.5.4"
                },
                {
                    "requirement_name": "Time Monitoring",
                    "requirement_type": "time",
                    "description": "Holding time verification",
                    "is_critical_limit": True,
                    "target_value": 15.0,
                    "tolerance_min": 15.0,
                    "tolerance_max": None,
                    "unit_of_measure": "seconds",
                    "monitoring_frequency": "continuous",
                    "is_mandatory": True,
                    "equipment_required": "Timer/chart recorder",
                    "measurement_method": "Electronic timing device",
                    "calibration_required": True,
                    "regulatory_reference": "ISO 22000:2018 Clause 8.5.4"
                }
            ],
            "fermentation": [
                {
                    "requirement_name": "pH Monitoring",
                    "requirement_type": "ph",
                    "description": "pH monitoring during fermentation",
                    "is_critical_limit": True,
                    "target_value": 4.5,
                    "tolerance_min": 4.2,
                    "tolerance_max": 4.8,
                    "unit_of_measure": "pH",
                    "monitoring_frequency": "every_30_minutes",
                    "is_mandatory": True,
                    "equipment_required": "Calibrated pH meter",
                    "measurement_method": "Electronic pH probe",
                    "calibration_required": True,
                    "regulatory_reference": "ISO 22000:2018 Clause 8.5.4"
                },
                {
                    "requirement_name": "Temperature Control",
                    "requirement_type": "temperature",
                    "description": "Fermentation temperature control",
                    "is_critical_limit": False,
                    "is_operational_limit": True,
                    "target_value": 43.0,
                    "tolerance_min": 41.0,
                    "tolerance_max": 45.0,
                    "unit_of_measure": "°C",
                    "monitoring_frequency": "hourly",
                    "is_mandatory": True,
                    "equipment_required": "Thermometer",
                    "measurement_method": "Temperature probe",
                    "calibration_required": True,
                    "regulatory_reference": "ISO 22000:2018 Clause 8.5.3"
                }
            ],
            "cooling": [
                {
                    "requirement_name": "Final Temperature Check",
                    "requirement_type": "temperature",
                    "description": "Verify final product temperature",
                    "is_critical_limit": False,
                    "is_operational_limit": True,
                    "target_value": 4.0,
                    "tolerance_min": None,
                    "tolerance_max": 4.0,
                    "unit_of_measure": "°C",
                    "monitoring_frequency": "end_of_process",
                    "is_mandatory": True,
                    "equipment_required": "Calibrated thermometer",
                    "measurement_method": "Digital thermometer",
                    "calibration_required": True,
                    "regulatory_reference": "ISO 22000:2018 Clause 8.5.3"
                }
            ],
            "storage": [
                {
                    "requirement_name": "Storage Temperature",
                    "requirement_type": "temperature",
                    "description": "Cold storage temperature monitoring",
                    "is_critical_limit": False,
                    "is_operational_limit": True,
                    "target_value": 4.0,
                    "tolerance_min": None,
                    "tolerance_max": 4.0,
                    "unit_of_measure": "°C",
                    "monitoring_frequency": "continuous",
                    "is_mandatory": True,
                    "equipment_required": "Temperature logger",
                    "measurement_method": "Continuous monitoring system",
                    "calibration_required": True,
                    "regulatory_reference": "ISO 22000:2018 Clause 8.5.1"
                }
            ]
        }
        
        # Map stage names to requirement types
        stage_mapping = {
            "htst pasteurization": "pasteurization",
            "pasteurization": "pasteurization",
            "fermentation": "fermentation",
            "acidification": "fermentation",
            "rapid cooling": "cooling",
            "cooling for inoculation": "cooling",
            "cooling and packaging": "cooling",
            "cold storage": "storage"
        }
        
        stage_key = stage_mapping.get(stage_name.lower(), "default")
        
        if stage_key in common_requirements:
            requirements = common_requirements[stage_key].copy()
            
            # Adjust critical limits based on CCP status
            if is_ccp:
                for req in requirements:
                    if not req.get("is_critical_limit"):
                        req["is_critical_limit"] = True
                        req["is_operational_limit"] = False
            
            return requirements
        
        # Default requirements for stages without specific monitoring
        return [
            {
                "requirement_name": "Visual Inspection",
                "requirement_type": "visual_inspection",
                "description": "Visual quality check",
                "is_critical_limit": False,
                "is_operational_limit": True,
                "monitoring_frequency": "per_batch",
                "is_mandatory": True,
                "equipment_required": "None",
                "measurement_method": "Visual observation",
                "calibration_required": False,
                "regulatory_reference": "ISO 22000:2018 Clause 8.5.2"
            }
        ]
    
    @staticmethod
    def get_template_by_product_type(product_type: str) -> List[Dict[str, Any]]:
        """
        Get stage template for a specific product type
        
        Args:
            product_type: The product type (fresh_milk, yoghurt, cheese, etc.)
            
        Returns:
            List of stage dictionaries for the product type
        """
        templates = {
            "fresh_milk": ISO22000StageTemplates.get_fresh_milk_stages(),
            "pasteurized_milk": ISO22000StageTemplates.get_fresh_milk_stages(),
            "yoghurt": ISO22000StageTemplates.get_yoghurt_stages(),
            "cheese": ISO22000StageTemplates.get_cheese_stages(),
        }
        
        return templates.get(product_type, [])
    
    @staticmethod
    def validate_iso_compliance(stages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that stages comply with ISO 22000:2018 requirements
        
        Args:
            stages: List of stage dictionaries to validate
            
        Returns:
            Validation result with compliance status and recommendations
        """
        validation_result = {
            "is_compliant": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check for at least one CCP
        has_ccp = any(stage.get("is_critical_control_point", False) for stage in stages)
        if not has_ccp:
            validation_result["warnings"].append(
                "No Critical Control Points (CCPs) identified. ISO 22000:2018 requires identification of CCPs where control is essential."
            )
        
        # Check for proper sequencing
        sequences = [stage.get("sequence_order", 0) for stage in stages]
        if sequences != sorted(sequences) or len(set(sequences)) != len(sequences):
            validation_result["errors"].append(
                "Stages must have unique, sequential order numbers starting from 1."
            )
            validation_result["is_compliant"] = False
        
        # Check for monitoring requirements on CCPs
        for stage in stages:
            if stage.get("is_critical_control_point", False):
                if not stage.get("completion_criteria", {}).get("mandatory_monitoring_required", False):
                    validation_result["errors"].append(
                        f"CCP stage '{stage.get('stage_name')}' must have mandatory monitoring requirements."
                    )
                    validation_result["is_compliant"] = False
        
        # Check for proper documentation
        for stage in stages:
            if not stage.get("stage_name"):
                validation_result["errors"].append("All stages must have a stage name.")
                validation_result["is_compliant"] = False
            
            if stage.get("is_critical_control_point", False) and not stage.get("stage_description"):
                validation_result["warnings"].append(
                    f"CCP stage '{stage.get('stage_name')}' should have a detailed description."
                )
        
        # Recommendations for better compliance
        validation_result["recommendations"].extend([
            "Ensure all CCPs have continuous or frequent monitoring requirements",
            "Document all critical limits with tolerance ranges",
            "Include regulatory references (ISO clauses) in stage notes",
            "Establish clear completion criteria for each stage",
            "Ensure traceability through all stages"
        ])
        
        return validation_result