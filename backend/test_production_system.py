# -*- coding: utf-8 -*-
"""
Test Script for Production System
Populates the system with sample data and tests all functionality
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample production data for testing"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Creating sample production data...")
    
    try:
        # Create sample batches first
        cursor.execute('''
            INSERT OR IGNORE INTO batches 
            (batch_number, product_type, quantity, unit, production_date, status, created_at)
            VALUES 
            ('BATCH-001', 'fresh_milk', 1000.0, 'L', '2025-01-15', 'completed', '2025-01-15 08:00:00'),
            ('BATCH-002', 'yoghurt', 500.0, 'L', '2025-01-16', 'completed', '2025-01-16 09:00:00'),
            ('BATCH-003', 'cheese', 200.0, 'kg', '2025-01-17', 'in_progress', '2025-01-17 07:00:00'),
            ('BATCH-004', 'fresh_milk', 1200.0, 'L', '2025-01-18', 'in_progress', '2025-01-18 08:30:00'),
            ('BATCH-005', 'mala', 300.0, 'L', '2025-01-19', 'pending', '2025-01-19 06:00:00')
        ''')
        
        # Get batch IDs
        cursor.execute("SELECT id FROM batches ORDER BY id")
        batch_ids = [row[0] for row in cursor.fetchall()]
        
        # Create sample production processes
        processes_data = [
            {
                'batch_id': batch_ids[0],
                'process_type': 'fresh_milk',
                'operator_id': 1,
                'status': 'completed',
                'start_time': '2025-01-15 08:00:00',
                'end_time': '2025-01-15 10:30:00',
                'spec': json.dumps({
                    'steps': [
                        {'type': 'heat', 'target_temp_c': 72.0, 'target_time_seconds': 15},
                        {'type': 'cool', 'target_temp_c': 4.0, 'target_time_seconds': 300}
                    ]
                })
            },
            {
                'batch_id': batch_ids[1],
                'process_type': 'yoghurt',
                'operator_id': 2,
                'status': 'completed',
                'start_time': '2025-01-16 09:00:00',
                'end_time': '2025-01-16 18:00:00',
                'spec': json.dumps({
                    'steps': [
                        {'type': 'heat', 'target_temp_c': 50.0, 'target_time_seconds': 600},
                        {'type': 'culture_addition', 'target_temp_c': 50.0},
                        {'type': 'ferment', 'target_temp_c': 45.0, 'target_time_seconds': 28800},
                        {'type': 'cool', 'target_temp_c': 4.0, 'target_time_seconds': 1800}
                    ]
                })
            },
            {
                'batch_id': batch_ids[2],
                'process_type': 'cheese',
                'operator_id': 1,
                'status': 'in_progress',
                'start_time': '2025-01-17 07:00:00',
                'end_time': None,
                'spec': json.dumps({
                    'steps': [
                        {'type': 'heat', 'target_temp_c': 90.0, 'target_time_seconds': 1800},
                        {'type': 'culture_addition', 'target_temp_c': 32.0},
                        {'type': 'coagulation', 'target_temp_c': 32.0, 'target_time_seconds': 3600},
                        {'type': 'cut_curd', 'target_temp_c': 32.0},
                        {'type': 'drain', 'target_temp_c': 32.0},
                        {'type': 'press', 'target_temp_c': 20.0, 'target_time_seconds': 7200},
                        {'type': 'age', 'target_temp_c': 12.0, 'target_time_seconds': 1209600}
                    ]
                })
            },
            {
                'batch_id': batch_ids[3],
                'process_type': 'fresh_milk',
                'operator_id': 2,
                'status': 'in_progress',
                'start_time': '2025-01-18 08:30:00',
                'end_time': None,
                'spec': json.dumps({
                    'steps': [
                        {'type': 'heat', 'target_temp_c': 72.0, 'target_time_seconds': 15},
                        {'type': 'cool', 'target_temp_c': 4.0, 'target_time_seconds': 300}
                    ]
                })
            }
        ]
        
        for process_data in processes_data:
            cursor.execute('''
                INSERT OR IGNORE INTO production_processes 
                (batch_id, process_type, operator_id, status, start_time, end_time, spec, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                process_data['batch_id'],
                process_data['process_type'],
                process_data['operator_id'],
                process_data['status'],
                process_data['start_time'],
                process_data['end_time'],
                process_data['spec'],
                process_data['start_time']
            ))
        
        # Get process IDs
        cursor.execute("SELECT id FROM production_processes ORDER BY id")
        process_ids = [row[0] for row in cursor.fetchall()]
        
        # Create sample process parameters
        parameters_data = [
            # Process 1 - Fresh Milk (completed)
            {'process_id': process_ids[0], 'parameter_name': 'pasteurization_temperature', 'parameter_value': 72.5, 'unit': '°C', 'target_value': 72.0, 'tolerance_min': 71.0, 'tolerance_max': 73.0, 'is_within_tolerance': True, 'recorded_at': '2025-01-15 08:15:00'},
            {'process_id': process_ids[0], 'parameter_name': 'pasteurization_time', 'parameter_value': 15.2, 'unit': 'seconds', 'target_value': 15.0, 'tolerance_min': 14.5, 'tolerance_max': 15.5, 'is_within_tolerance': True, 'recorded_at': '2025-01-15 08:15:15'},
            {'process_id': process_ids[0], 'parameter_name': 'cooling_temperature', 'parameter_value': 4.2, 'unit': '°C', 'target_value': 4.0, 'tolerance_min': 3.0, 'tolerance_max': 5.0, 'is_within_tolerance': True, 'recorded_at': '2025-01-15 08:20:00'},
            
            # Process 2 - Yoghurt (completed)
            {'process_id': process_ids[1], 'parameter_name': 'heating_temperature', 'parameter_value': 50.5, 'unit': '°C', 'target_value': 50.0, 'tolerance_min': 48.0, 'tolerance_max': 52.0, 'is_within_tolerance': True, 'recorded_at': '2025-01-16 09:10:00'},
            {'process_id': process_ids[1], 'parameter_name': 'fermentation_temperature', 'parameter_value': 45.2, 'unit': '°C', 'target_value': 45.0, 'tolerance_min': 43.0, 'tolerance_max': 47.0, 'is_within_tolerance': True, 'recorded_at': '2025-01-16 10:00:00'},
            {'process_id': process_ids[1], 'parameter_name': 'fermentation_time', 'parameter_value': 28800, 'unit': 'seconds', 'target_value': 28800, 'tolerance_min': 28000, 'tolerance_max': 29600, 'is_within_tolerance': True, 'recorded_at': '2025-01-16 18:00:00'},
            
            # Process 3 - Cheese (in progress) - with some deviations
            {'process_id': process_ids[2], 'parameter_name': 'pasteurization_temperature', 'parameter_value': 89.5, 'unit': '°C', 'target_value': 90.0, 'tolerance_min': 88.0, 'tolerance_max': 92.0, 'is_within_tolerance': True, 'recorded_at': '2025-01-17 07:30:00'},
            {'process_id': process_ids[2], 'parameter_name': 'coagulation_temperature', 'parameter_value': 31.8, 'unit': '°C', 'target_value': 32.0, 'tolerance_min': 31.0, 'tolerance_max': 33.0, 'is_within_tolerance': True, 'recorded_at': '2025-01-17 09:00:00'},
            {'process_id': process_ids[2], 'parameter_name': 'coagulation_time', 'parameter_value': 3500, 'unit': 'seconds', 'target_value': 3600, 'tolerance_min': 3500, 'tolerance_max': 3700, 'is_within_tolerance': False, 'recorded_at': '2025-01-17 10:00:00'},
            
            # Process 4 - Fresh Milk (in progress) - with deviation
            {'process_id': process_ids[3], 'parameter_name': 'pasteurization_temperature', 'parameter_value': 70.5, 'unit': '°C', 'target_value': 72.0, 'tolerance_min': 71.0, 'tolerance_max': 73.0, 'is_within_tolerance': False, 'recorded_at': '2025-01-18 08:45:00'},
        ]
        
        for param_data in parameters_data:
            cursor.execute('''
                INSERT OR IGNORE INTO process_parameters 
                (process_id, parameter_name, parameter_value, unit, target_value, tolerance_min, tolerance_max, is_within_tolerance, recorded_at, recorded_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                param_data['process_id'],
                param_data['parameter_name'],
                param_data['parameter_value'],
                param_data['unit'],
                param_data['target_value'],
                param_data['tolerance_min'],
                param_data['tolerance_max'],
                param_data['is_within_tolerance'],
                param_data['recorded_at'],
                1
            ))
        
        # Create sample deviations (for out-of-tolerance parameters)
        deviations_data = [
            {
                'process_id': process_ids[2],
                'deviation_type': 'coagulation_time',
                'expected_value': 3600,
                'actual_value': 3500,
                'deviation_percent': -2.78,
                'severity': 'low',
                'impact_assessment': 'Slightly shorter coagulation time may affect cheese texture',
                'corrective_action': 'Monitor cheese quality and adjust process if needed',
                'resolved': False,
                'created_at': '2025-01-17 10:00:00',
                'created_by': 1
            },
            {
                'process_id': process_ids[3],
                'deviation_type': 'pasteurization_temperature',
                'expected_value': 72.0,
                'actual_value': 70.5,
                'deviation_percent': -2.08,
                'severity': 'critical',
                'impact_assessment': 'Temperature below minimum for HTST pasteurization',
                'corrective_action': 'Immediate process diversion required',
                'resolved': False,
                'created_at': '2025-01-18 08:45:00',
                'created_by': 1
            }
        ]
        
        for dev_data in deviations_data:
            cursor.execute('''
                INSERT OR IGNORE INTO process_deviations 
                (process_id, deviation_type, expected_value, actual_value, deviation_percent, severity, impact_assessment, corrective_action, resolved, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dev_data['process_id'],
                dev_data['deviation_type'],
                dev_data['expected_value'],
                dev_data['actual_value'],
                dev_data['deviation_percent'],
                dev_data['severity'],
                dev_data['impact_assessment'],
                dev_data['corrective_action'],
                dev_data['resolved'],
                dev_data['created_at'],
                dev_data['created_by']
            ))
        
        # Create sample alerts
        alerts_data = [
            {
                'process_id': process_ids[3],
                'alert_type': 'temperature_low',
                'alert_level': 'critical',
                'message': 'Pasteurization temperature below minimum threshold',
                'parameter_value': 70.5,
                'threshold_value': 71.0,
                'acknowledged': False,
                'created_at': '2025-01-18 08:45:00',
                'created_by': 1
            },
            {
                'process_id': process_ids[2],
                'alert_type': 'time_deviation',
                'alert_level': 'warning',
                'message': 'Coagulation time slightly shorter than target',
                'parameter_value': 3500,
                'threshold_value': 3600,
                'acknowledged': True,
                'acknowledged_at': '2025-01-17 10:15:00',
                'acknowledged_by': 1,
                'created_at': '2025-01-17 10:00:00',
                'created_by': 1
            }
        ]
        
        for alert_data in alerts_data:
            cursor.execute('''
                INSERT OR IGNORE INTO process_alerts 
                (process_id, alert_type, alert_level, message, parameter_value, threshold_value, acknowledged, acknowledged_at, acknowledged_by, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert_data['process_id'],
                alert_data['alert_type'],
                alert_data['alert_level'],
                alert_data['message'],
                alert_data['parameter_value'],
                alert_data['threshold_value'],
                alert_data['acknowledged'],
                alert_data.get('acknowledged_at'),
                alert_data.get('acknowledged_by'),
                alert_data['created_at'],
                alert_data['created_by']
            ))
        
        # Create sample yield records
        yield_data = [
            {'process_id': process_ids[0], 'output_qty': 980.0, 'expected_qty': 1000.0, 'unit': 'L', 'overrun_percent': -2.0},
            {'process_id': process_ids[1], 'output_qty': 485.0, 'expected_qty': 500.0, 'unit': 'L', 'overrun_percent': -3.0},
        ]
        
        for yield_record in yield_data:
            cursor.execute('''
                INSERT OR IGNORE INTO yield_records 
                (process_id, output_qty, expected_qty, unit, overrun_percent, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                yield_record['process_id'],
                yield_record['output_qty'],
                yield_record['expected_qty'],
                yield_record['unit'],
                yield_record['overrun_percent'],
                datetime.now().isoformat()
            ))
        
        # Create sample process templates
        templates_data = [
            {
                'template_name': 'Fresh Milk HTST Process',
                'product_type': 'fresh_milk',
                'description': 'Standard HTST pasteurization process for fresh milk',
                'steps': json.dumps([
                    {'step_type': 'heat', 'sequence': 1, 'target_temp_c': 72.0, 'target_time_seconds': 15, 'tolerance_c': 1.0, 'required': True},
                    {'step_type': 'cool', 'sequence': 2, 'target_temp_c': 4.0, 'target_time_seconds': 300, 'tolerance_c': 2.0, 'required': True},
                    {'step_type': 'transfer_cold_room', 'sequence': 3, 'target_temp_c': 4.0, 'tolerance_c': 1.0, 'required': True}
                ]),
                'is_active': True,
                'created_by': 1
            },
            {
                'template_name': 'Yoghurt Fermentation Process',
                'product_type': 'yoghurt',
                'description': 'Standard yoghurt fermentation process',
                'steps': json.dumps([
                    {'step_type': 'heat', 'sequence': 1, 'target_temp_c': 50.0, 'target_time_seconds': 600, 'tolerance_c': 2.0, 'required': True},
                    {'step_type': 'culture_addition', 'sequence': 2, 'target_temp_c': 50.0, 'tolerance_c': 1.0, 'required': True},
                    {'step_type': 'ferment', 'sequence': 3, 'target_temp_c': 45.0, 'target_time_seconds': 28800, 'tolerance_c': 2.0, 'required': True},
                    {'step_type': 'cool', 'sequence': 4, 'target_temp_c': 4.0, 'target_time_seconds': 1800, 'tolerance_c': 1.0, 'required': True}
                ]),
                'is_active': True,
                'created_by': 1
            },
            {
                'template_name': 'Cheese Production Process',
                'product_type': 'cheese',
                'description': 'Standard cheese production process with aging',
                'steps': json.dumps([
                    {'step_type': 'heat', 'sequence': 1, 'target_temp_c': 90.0, 'target_time_seconds': 1800, 'tolerance_c': 2.0, 'required': True},
                    {'step_type': 'culture_addition', 'sequence': 2, 'target_temp_c': 32.0, 'tolerance_c': 1.0, 'required': True},
                    {'step_type': 'coagulation', 'sequence': 3, 'target_temp_c': 32.0, 'target_time_seconds': 3600, 'tolerance_c': 1.0, 'required': True},
                    {'step_type': 'cut_curd', 'sequence': 4, 'target_temp_c': 32.0, 'tolerance_c': 1.0, 'required': True},
                    {'step_type': 'drain', 'sequence': 5, 'target_temp_c': 32.0, 'tolerance_c': 2.0, 'required': True},
                    {'step_type': 'press', 'sequence': 6, 'target_temp_c': 20.0, 'target_time_seconds': 7200, 'tolerance_c': 2.0, 'required': True},
                    {'step_type': 'age', 'sequence': 7, 'target_temp_c': 12.0, 'target_time_seconds': 1209600, 'tolerance_c': 2.0, 'required': True}
                ]),
                'is_active': True,
                'created_by': 1
            }
        ]
        
        for template_data in templates_data:
            cursor.execute('''
                INSERT OR IGNORE INTO process_templates 
                (template_name, product_type, description, steps, is_active, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                template_data['template_name'],
                template_data['product_type'],
                template_data['description'],
                template_data['steps'],
                template_data['is_active'],
                template_data['created_by'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        print("✅ Sample production data created successfully!")
        
        # Show statistics
        cursor.execute("SELECT COUNT(*) FROM production_processes")
        process_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM process_parameters")
        param_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM process_deviations")
        deviation_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM process_alerts")
        alert_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM process_templates")
        template_count = cursor.fetchone()[0]
        
        print(f"📊 Created:")
        print(f"   - {process_count} production processes")
        print(f"   - {param_count} process parameters")
        print(f"   - {deviation_count} process deviations")
        print(f"   - {alert_count} process alerts")
        print(f"   - {template_count} process templates")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_sample_data()
