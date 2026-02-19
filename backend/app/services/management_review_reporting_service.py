"""
Management Review Reporting Service
Provides comprehensive reporting capabilities for ISO 22000:2018 compliance and analytics
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, case
import json

from app.models.management_review import (
    ManagementReview, ReviewAction, ManagementReviewInput, ManagementReviewOutput,
    ManagementReviewStatus, ActionStatus, ReviewInputType, ReviewOutputType,
    ManagementReviewType, ActionPriority
)
from app.models.user import User
from app.services.management_review_data_aggregation_service import ManagementReviewDataAggregationService


class ManagementReviewReportingService:
    """Service for generating comprehensive management review reports"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_aggregation_service = ManagementReviewDataAggregationService(db)
    
    # ==================== EXECUTIVE SUMMARY REPORTS ====================
    
    def generate_executive_summary(self, date_range_start: Optional[datetime] = None, 
                                 date_range_end: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate executive summary report for management reviews"""
        if not date_range_end:
            date_range_end = datetime.utcnow()
        if not date_range_start:
            date_range_start = date_range_end - timedelta(days=365)  # Last year
        
        # Get reviews in date range
        reviews_query = self.db.query(ManagementReview).filter(
            and_(
                ManagementReview.created_at >= date_range_start,
                ManagementReview.created_at <= date_range_end
            )
        )
        
        total_reviews = reviews_query.count()
        completed_reviews = reviews_query.filter(ManagementReview.status == ManagementReviewStatus.COMPLETED).count()
        in_progress_reviews = reviews_query.filter(ManagementReview.status == ManagementReviewStatus.IN_PROGRESS).count()
        planned_reviews = reviews_query.filter(ManagementReview.status == ManagementReviewStatus.PLANNED).count()
        
        # Calculate completion rate
        completion_rate = (completed_reviews / total_reviews * 100) if total_reviews > 0 else 0
        
        # Get effectiveness scores
        effectiveness_scores = [r.review_effectiveness_score for r in reviews_query.all() 
                              if r.review_effectiveness_score is not None]
        avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0
        
        # Get action statistics
        actions_query = self.db.query(ReviewAction).join(ManagementReview).filter(
            and_(
                ManagementReview.created_at >= date_range_start,
                ManagementReview.created_at <= date_range_end
            )
        )
        
        total_actions = actions_query.count()
        completed_actions = actions_query.filter(ReviewAction.completed == True).count()
        overdue_actions = actions_query.filter(
            and_(
                ReviewAction.due_date < datetime.utcnow(),
                ReviewAction.completed == False
            )
        ).count()
        
        action_completion_rate = (completed_actions / total_actions * 100) if total_actions > 0 else 0
        
        # Get compliance statistics
        compliance_scores = []
        for review in reviews_query.all():
            if review.status == ManagementReviewStatus.COMPLETED:
                # Calculate basic compliance score based on inputs and outputs
                inputs_count = len(review.inputs_data) if hasattr(review, 'inputs_data') else 0
                outputs_count = len(review.outputs_data) if hasattr(review, 'outputs_data') else 0
                compliance_score = min(((inputs_count * 10) + (outputs_count * 15)) / 25 * 100, 100)
                compliance_scores.append(compliance_score)
        
        avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
        
        return {
            "period": {
                "start_date": date_range_start.isoformat(),
                "end_date": date_range_end.isoformat(),
                "days": (date_range_end - date_range_start).days
            },
            "review_statistics": {
                "total_reviews": total_reviews,
                "completed_reviews": completed_reviews,
                "in_progress_reviews": in_progress_reviews,
                "planned_reviews": planned_reviews,
                "completion_rate": round(completion_rate, 2)
            },
            "effectiveness_metrics": {
                "average_effectiveness_score": round(avg_effectiveness, 2),
                "effectiveness_trend": "stable",  # Would calculate from historical data
                "reviews_with_scores": len(effectiveness_scores)
            },
            "action_metrics": {
                "total_actions": total_actions,
                "completed_actions": completed_actions,
                "overdue_actions": overdue_actions,
                "action_completion_rate": round(action_completion_rate, 2)
            },
            "compliance_metrics": {
                "average_compliance_score": round(avg_compliance, 2),
                "compliant_reviews": len([s for s in compliance_scores if s >= 80]),
                "non_compliant_reviews": len([s for s in compliance_scores if s < 80])
            },
            "key_insights": self._generate_key_insights(total_reviews, completion_rate, avg_effectiveness, action_completion_rate),
            "recommendations": self._generate_executive_recommendations(completion_rate, avg_effectiveness, action_completion_rate, overdue_actions)
        }
    
    def generate_iso_compliance_report(self, date_range_start: Optional[datetime] = None,
                                     date_range_end: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate detailed ISO 22000:2018 compliance report"""
        if not date_range_end:
            date_range_end = datetime.utcnow()
        if not date_range_start:
            date_range_start = date_range_end - timedelta(days=365)
        
        reviews = self.db.query(ManagementReview).filter(
            and_(
                ManagementReview.created_at >= date_range_start,
                ManagementReview.created_at <= date_range_end
            )
        ).all()
        
        # Required inputs per ISO 22000:2018
        required_inputs = [
            ReviewInputType.AUDIT_RESULTS,
            ReviewInputType.NC_CAPA_STATUS,
            ReviewInputType.SUPPLIER_PERFORMANCE,
            ReviewInputType.HACCP_PERFORMANCE,
            ReviewInputType.PRP_PERFORMANCE,
            ReviewInputType.RISK_ASSESSMENT,
            ReviewInputType.PREVIOUS_ACTIONS
        ]
        
        # Required outputs per ISO 22000:2018
        required_outputs = [
            ReviewOutputType.IMPROVEMENT_ACTION,
            ReviewOutputType.RESOURCE_ALLOCATION,
            ReviewOutputType.SYSTEM_CHANGE
        ]
        
        compliance_details = []
        overall_compliance_scores = []
        
        for review in reviews:
            if review.status == ManagementReviewStatus.COMPLETED:
                # Check inputs
                present_inputs = [inp.input_type for inp in review.inputs_data] if hasattr(review, 'inputs_data') else []
                missing_inputs = [inp.value for inp in required_inputs if inp not in present_inputs]
                input_compliance = (len(required_inputs) - len(missing_inputs)) / len(required_inputs) * 100
                
                # Check outputs
                present_outputs = [out.output_type for out in review.outputs_data] if hasattr(review, 'outputs_data') else []
                missing_outputs = [out.value for out in required_outputs if out not in present_outputs]
                output_compliance = (len(required_outputs) - len(missing_outputs)) / len(required_outputs) * 100
                
                # Overall compliance
                overall_compliance = (input_compliance + output_compliance) / 2
                overall_compliance_scores.append(overall_compliance)
                
                compliance_details.append({
                    "review_id": review.id,
                    "review_title": review.title,
                    "review_date": review.review_date.isoformat() if review.review_date else None,
                    "input_compliance": round(input_compliance, 2),
                    "output_compliance": round(output_compliance, 2),
                    "overall_compliance": round(overall_compliance, 2),
                    "missing_inputs": missing_inputs,
                    "missing_outputs": missing_outputs,
                    "policy_reviewed": review.food_safety_policy_reviewed,
                    "objectives_reviewed": review.food_safety_objectives_reviewed,
                    "fsms_changes_required": review.fsms_changes_required
                })
        
        avg_compliance = sum(overall_compliance_scores) / len(overall_compliance_scores) if overall_compliance_scores else 0
        
        return {
            "period": {
                "start_date": date_range_start.isoformat(),
                "end_date": date_range_end.isoformat()
            },
            "overall_compliance": {
                "average_compliance_score": round(avg_compliance, 2),
                "fully_compliant_reviews": len([s for s in overall_compliance_scores if s >= 95]),
                "partially_compliant_reviews": len([s for s in overall_compliance_scores if 80 <= s < 95]),
                "non_compliant_reviews": len([s for s in overall_compliance_scores if s < 80])
            },
            "input_compliance_analysis": self._analyze_input_compliance(reviews, required_inputs),
            "output_compliance_analysis": self._analyze_output_compliance(reviews, required_outputs),
            "review_compliance_details": compliance_details,
            "compliance_trends": self._calculate_compliance_trends(reviews),
            "improvement_recommendations": self._generate_compliance_recommendations(compliance_details)
        }
    
    # ==================== PERFORMANCE ANALYTICS REPORTS ====================
    
    def generate_effectiveness_analysis_report(self, date_range_start: Optional[datetime] = None,
                                             date_range_end: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate detailed effectiveness analysis report"""
        if not date_range_end:
            date_range_end = datetime.utcnow()
        if not date_range_start:
            date_range_start = date_range_end - timedelta(days=365)
        
        reviews = self.db.query(ManagementReview).filter(
            and_(
                ManagementReview.created_at >= date_range_start,
                ManagementReview.created_at <= date_range_end,
                ManagementReview.review_effectiveness_score.isnot(None)
            )
        ).all()
        
        effectiveness_data = []
        for review in reviews:
            # Get detailed metrics
            inputs_count = len(review.inputs_data) if hasattr(review, 'inputs_data') else 0
            outputs_count = len(review.outputs_data) if hasattr(review, 'outputs_data') else 0
            actions_count = len(review.actions) if hasattr(review, 'actions') else 0
            completed_actions = len([a for a in review.actions if a.completed]) if hasattr(review, 'actions') else 0
            
            effectiveness_data.append({
                "review_id": review.id,
                "review_title": review.title,
                "review_date": review.review_date.isoformat() if review.review_date else None,
                "effectiveness_score": review.review_effectiveness_score,
                "inputs_count": inputs_count,
                "outputs_count": outputs_count,
                "actions_count": actions_count,
                "completed_actions": completed_actions,
                "action_completion_rate": (completed_actions / actions_count * 100) if actions_count > 0 else 0
            })
        
        # Calculate statistics
        effectiveness_scores = [r.review_effectiveness_score for r in reviews]
        avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0
        
        return {
            "period": {
                "start_date": date_range_start.isoformat(),
                "end_date": date_range_end.isoformat()
            },
            "effectiveness_overview": {
                "total_reviews_analyzed": len(reviews),
                "average_effectiveness_score": round(avg_effectiveness, 2),
                "highest_score": max(effectiveness_scores) if effectiveness_scores else 0,
                "lowest_score": min(effectiveness_scores) if effectiveness_scores else 0,
                "excellent_reviews": len([s for s in effectiveness_scores if s >= 8]),
                "good_reviews": len([s for s in effectiveness_scores if 6 <= s < 8]),
                "needs_improvement_reviews": len([s for s in effectiveness_scores if s < 6])
            },
            "effectiveness_details": effectiveness_data,
            "effectiveness_factors": self._analyze_effectiveness_factors(effectiveness_data),
            "improvement_opportunities": self._identify_effectiveness_improvements(effectiveness_data)
        }
    
    def generate_action_tracking_report(self, date_range_start: Optional[datetime] = None,
                                      date_range_end: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate comprehensive action tracking report"""
        if not date_range_end:
            date_range_end = datetime.utcnow()
        if not date_range_start:
            date_range_start = date_range_end - timedelta(days=365)
        
        actions_query = self.db.query(ReviewAction).join(ManagementReview).filter(
            and_(
                ManagementReview.created_at >= date_range_start,
                ManagementReview.created_at <= date_range_end
            )
        )
        
        actions = actions_query.all()
        
        # Status distribution
        status_distribution = {}
        for status in ActionStatus:
            status_distribution[status.value] = len([a for a in actions if a.status == status])
        
        # Priority distribution
        priority_distribution = {}
        for priority in ActionPriority:
            priority_distribution[priority.value] = len([a for a in actions if a.priority == priority])
        
        # Completion analysis
        total_actions = len(actions)
        completed_actions = len([a for a in actions if a.completed])
        overdue_actions = len([a for a in actions if a.due_date and a.due_date < datetime.utcnow() and not a.completed])
        
        # Average completion time
        completed_with_dates = [a for a in actions if a.completed and a.completed_at and a.created_at]
        avg_completion_days = 0
        if completed_with_dates:
            completion_times = [(a.completed_at - a.created_at).days for a in completed_with_dates]
            avg_completion_days = sum(completion_times) / len(completion_times)
        
        # Action type analysis
        action_types = {}
        for action in actions:
            if action.action_type:
                action_types[action.action_type.value] = action_types.get(action.action_type.value, 0) + 1
        
        return {
            "period": {
                "start_date": date_range_start.isoformat(),
                "end_date": date_range_end.isoformat()
            },
            "action_overview": {
                "total_actions": total_actions,
                "completed_actions": completed_actions,
                "in_progress_actions": status_distribution.get("in_progress", 0),
                "overdue_actions": overdue_actions,
                "completion_rate": round((completed_actions / total_actions * 100) if total_actions > 0 else 0, 2),
                "average_completion_days": round(avg_completion_days, 1)
            },
            "status_distribution": status_distribution,
            "priority_distribution": priority_distribution,
            "action_type_distribution": action_types,
            "overdue_analysis": self._analyze_overdue_actions(actions),
            "performance_by_assignee": self._analyze_action_performance_by_assignee(actions),
            "recommendations": self._generate_action_tracking_recommendations(actions, overdue_actions, completion_rate=completed_actions / total_actions * 100 if total_actions > 0 else 0)
        }
    
    # ==================== TREND ANALYSIS REPORTS ====================
    
    def generate_trend_analysis_report(self, months_back: int = 12) -> Dict[str, Any]:
        """Generate trend analysis report showing performance over time"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months_back * 30)
        
        # Monthly data points
        monthly_data = []
        for i in range(months_back):
            month_start = end_date - timedelta(days=(i + 1) * 30)
            month_end = end_date - timedelta(days=i * 30)
            
            reviews = self.db.query(ManagementReview).filter(
                and_(
                    ManagementReview.created_at >= month_start,
                    ManagementReview.created_at < month_end
                )
            ).all()
            
            completed_reviews = [r for r in reviews if r.status == ManagementReviewStatus.COMPLETED]
            effectiveness_scores = [r.review_effectiveness_score for r in completed_reviews if r.review_effectiveness_score]
            
            # Actions for this month
            actions = self.db.query(ReviewAction).join(ManagementReview).filter(
                and_(
                    ManagementReview.created_at >= month_start,
                    ManagementReview.created_at < month_end
                )
            ).all()
            
            completed_actions = [a for a in actions if a.completed]
            
            monthly_data.append({
                "month": month_start.strftime("%Y-%m"),
                "total_reviews": len(reviews),
                "completed_reviews": len(completed_reviews),
                "avg_effectiveness": sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0,
                "total_actions": len(actions),
                "completed_actions": len(completed_actions),
                "action_completion_rate": len(completed_actions) / len(actions) * 100 if actions else 0
            })
        
        monthly_data.reverse()  # Chronological order
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "months_analyzed": months_back
            },
            "monthly_trends": monthly_data,
            "trend_analysis": {
                "review_completion_trend": self._calculate_trend([d["completed_reviews"] for d in monthly_data]),
                "effectiveness_trend": self._calculate_trend([d["avg_effectiveness"] for d in monthly_data if d["avg_effectiveness"] > 0]),
                "action_completion_trend": self._calculate_trend([d["action_completion_rate"] for d in monthly_data])
            },
            "seasonal_patterns": self._identify_seasonal_patterns(monthly_data),
            "forecasting": self._generate_forecasting_insights(monthly_data)
        }
    
    # ==================== UTILITY METHODS ====================
    
    def _generate_key_insights(self, total_reviews: int, completion_rate: float, 
                             avg_effectiveness: float, action_completion_rate: float) -> List[str]:
        """Generate key insights for executive summary"""
        insights = []
        
        if completion_rate >= 90:
            insights.append("Excellent review completion rate indicates strong management commitment")
        elif completion_rate < 70:
            insights.append("Low review completion rate requires management attention")
        
        if avg_effectiveness >= 8:
            insights.append("High effectiveness scores demonstrate valuable review outcomes")
        elif avg_effectiveness < 6:
            insights.append("Effectiveness scores indicate need for review process improvement")
        
        if action_completion_rate >= 85:
            insights.append("Strong action completion rate shows effective follow-through")
        elif action_completion_rate < 70:
            insights.append("Action completion rate needs improvement for better outcomes")
        
        if total_reviews == 0:
            insights.append("No management reviews conducted in this period - immediate action required")
        
        return insights
    
    def _generate_executive_recommendations(self, completion_rate: float, avg_effectiveness: float,
                                          action_completion_rate: float, overdue_actions: int) -> List[str]:
        """Generate recommendations for executive summary"""
        recommendations = []
        
        if completion_rate < 80:
            recommendations.append("Implement automated review scheduling and reminders")
        
        if avg_effectiveness < 7:
            recommendations.append("Enhance review preparation with better input data collection")
            recommendations.append("Provide training on effective review facilitation")
        
        if action_completion_rate < 75:
            recommendations.append("Implement stronger action item tracking and accountability")
        
        if overdue_actions > 0:
            recommendations.append(f"Address {overdue_actions} overdue actions immediately")
        
        recommendations.append("Continue monitoring performance indicators monthly")
        
        return recommendations
    
    def _analyze_input_compliance(self, reviews: List[ManagementReview], 
                                required_inputs: List[ReviewInputType]) -> Dict[str, Any]:
        """Analyze input compliance across reviews"""
        input_coverage = {}
        for input_type in required_inputs:
            input_coverage[input_type.value] = 0
        
        for review in reviews:
            if hasattr(review, 'inputs_data'):
                for input_record in review.inputs_data:
                    if input_record.input_type in required_inputs:
                        input_coverage[input_record.input_type.value] += 1
        
        total_reviews = len([r for r in reviews if r.status == ManagementReviewStatus.COMPLETED])
        
        return {
            "input_coverage_rates": {k: round(v / total_reviews * 100, 2) if total_reviews > 0 else 0 
                                   for k, v in input_coverage.items()},
            "most_covered_inputs": sorted(input_coverage.items(), key=lambda x: x[1], reverse=True)[:3],
            "least_covered_inputs": sorted(input_coverage.items(), key=lambda x: x[1])[:3]
        }
    
    def _analyze_output_compliance(self, reviews: List[ManagementReview],
                                 required_outputs: List[ReviewOutputType]) -> Dict[str, Any]:
        """Analyze output compliance across reviews"""
        output_coverage = {}
        for output_type in required_outputs:
            output_coverage[output_type.value] = 0
        
        for review in reviews:
            if hasattr(review, 'outputs_data'):
                for output_record in review.outputs_data:
                    if output_record.output_type in required_outputs:
                        output_coverage[output_record.output_type.value] += 1
        
        total_reviews = len([r for r in reviews if r.status == ManagementReviewStatus.COMPLETED])
        
        return {
            "output_coverage_rates": {k: round(v / total_reviews * 100, 2) if total_reviews > 0 else 0 
                                    for k, v in output_coverage.items()},
            "most_generated_outputs": sorted(output_coverage.items(), key=lambda x: x[1], reverse=True)[:3],
            "least_generated_outputs": sorted(output_coverage.items(), key=lambda x: x[1])[:3]
        }
    
    def _calculate_compliance_trends(self, reviews: List[ManagementReview]) -> Dict[str, Any]:
        """Calculate compliance trends over time"""
        # This would analyze compliance over time periods
        return {
            "trend_direction": "stable",
            "improvement_rate": 0,
            "risk_areas": []
        }
    
    def _generate_compliance_recommendations(self, compliance_details: List[Dict]) -> List[str]:
        """Generate compliance improvement recommendations"""
        recommendations = []
        
        # Analyze common missing inputs/outputs
        all_missing_inputs = []
        all_missing_outputs = []
        
        for detail in compliance_details:
            all_missing_inputs.extend(detail.get("missing_inputs", []))
            all_missing_outputs.extend(detail.get("missing_outputs", []))
        
        # Find most common missing items
        if all_missing_inputs:
            from collections import Counter
            common_missing_inputs = Counter(all_missing_inputs).most_common(3)
            for input_type, count in common_missing_inputs:
                recommendations.append(f"Improve collection of {input_type} data (missing in {count} reviews)")
        
        if all_missing_outputs:
            from collections import Counter
            common_missing_outputs = Counter(all_missing_outputs).most_common(3)
            for output_type, count in common_missing_outputs:
                recommendations.append(f"Ensure {output_type} decisions are documented (missing in {count} reviews)")
        
        return recommendations
    
    def _analyze_effectiveness_factors(self, effectiveness_data: List[Dict]) -> Dict[str, Any]:
        """Analyze factors contributing to effectiveness"""
        # Correlate effectiveness scores with various factors
        high_effectiveness = [d for d in effectiveness_data if d["effectiveness_score"] >= 8]
        low_effectiveness = [d for d in effectiveness_data if d["effectiveness_score"] < 6]
        
        return {
            "high_effectiveness_characteristics": {
                "avg_inputs": sum(d["inputs_count"] for d in high_effectiveness) / len(high_effectiveness) if high_effectiveness else 0,
                "avg_outputs": sum(d["outputs_count"] for d in high_effectiveness) / len(high_effectiveness) if high_effectiveness else 0,
                "avg_action_completion": sum(d["action_completion_rate"] for d in high_effectiveness) / len(high_effectiveness) if high_effectiveness else 0
            },
            "low_effectiveness_characteristics": {
                "avg_inputs": sum(d["inputs_count"] for d in low_effectiveness) / len(low_effectiveness) if low_effectiveness else 0,
                "avg_outputs": sum(d["outputs_count"] for d in low_effectiveness) / len(low_effectiveness) if low_effectiveness else 0,
                "avg_action_completion": sum(d["action_completion_rate"] for d in low_effectiveness) / len(low_effectiveness) if low_effectiveness else 0
            }
        }
    
    def _identify_effectiveness_improvements(self, effectiveness_data: List[Dict]) -> List[str]:
        """Identify opportunities for effectiveness improvement"""
        improvements = []
        
        low_effectiveness_reviews = [d for d in effectiveness_data if d["effectiveness_score"] < 6]
        
        if low_effectiveness_reviews:
            avg_inputs = sum(d["inputs_count"] for d in low_effectiveness_reviews) / len(low_effectiveness_reviews)
            if avg_inputs < 5:
                improvements.append("Increase input data collection for better-informed reviews")
            
            avg_action_completion = sum(d["action_completion_rate"] for d in low_effectiveness_reviews) / len(low_effectiveness_reviews)
            if avg_action_completion < 70:
                improvements.append("Improve action item follow-through and completion tracking")
        
        return improvements
    
    def _analyze_overdue_actions(self, actions: List[ReviewAction]) -> Dict[str, Any]:
        """Analyze overdue actions in detail"""
        overdue_actions = [a for a in actions if a.due_date and a.due_date < datetime.utcnow() and not a.completed]
        
        if not overdue_actions:
            return {"total_overdue": 0}
        
        # Analyze by days overdue
        days_overdue = [(datetime.utcnow() - a.due_date).days for a in overdue_actions]
        
        return {
            "total_overdue": len(overdue_actions),
            "avg_days_overdue": sum(days_overdue) / len(days_overdue),
            "max_days_overdue": max(days_overdue),
            "overdue_by_priority": {
                priority.value: len([a for a in overdue_actions if a.priority == priority])
                for priority in ActionPriority
            }
        }
    
    def _analyze_action_performance_by_assignee(self, actions: List[ReviewAction]) -> Dict[str, Any]:
        """Analyze action performance by assignee"""
        assignee_performance = {}
        
        for action in actions:
            if action.assigned_to:
                if action.assigned_to not in assignee_performance:
                    assignee_performance[action.assigned_to] = {
                        "total_actions": 0,
                        "completed_actions": 0,
                        "overdue_actions": 0
                    }
                
                assignee_performance[action.assigned_to]["total_actions"] += 1
                if action.completed:
                    assignee_performance[action.assigned_to]["completed_actions"] += 1
                elif action.due_date and action.due_date < datetime.utcnow():
                    assignee_performance[action.assigned_to]["overdue_actions"] += 1
        
        # Calculate completion rates
        for assignee_id, stats in assignee_performance.items():
            stats["completion_rate"] = (stats["completed_actions"] / stats["total_actions"] * 100) if stats["total_actions"] > 0 else 0
        
        return assignee_performance
    
    def _generate_action_tracking_recommendations(self, actions: List[ReviewAction], 
                                                overdue_actions: int, completion_rate: float) -> List[str]:
        """Generate action tracking recommendations"""
        recommendations = []
        
        if completion_rate < 75:
            recommendations.append("Implement automated action item reminders")
            recommendations.append("Review action assignment process for clarity")
        
        if overdue_actions > 0:
            recommendations.append(f"Address {overdue_actions} overdue actions immediately")
            recommendations.append("Implement escalation procedures for overdue items")
        
        # Analyze action types
        high_priority_actions = [a for a in actions if a.priority == ActionPriority.HIGH or a.priority == ActionPriority.CRITICAL]
        if high_priority_actions:
            high_priority_completion = len([a for a in high_priority_actions if a.completed]) / len(high_priority_actions) * 100
            if high_priority_completion < 85:
                recommendations.append("Focus on improving completion of high-priority actions")
        
        return recommendations
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))
        
        # Calculate slope
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _identify_seasonal_patterns(self, monthly_data: List[Dict]) -> Dict[str, Any]:
        """Identify seasonal patterns in the data"""
        # This would analyze seasonal patterns
        return {
            "peak_months": [],
            "low_months": [],
            "seasonal_factors": []
        }
    
    def _generate_forecasting_insights(self, monthly_data: List[Dict]) -> Dict[str, Any]:
        """Generate forecasting insights based on trends"""
        return {
            "next_month_prediction": {
                "expected_reviews": 0,
                "confidence_level": "low"
            },
            "recommendations": [
                "Continue monitoring monthly trends",
                "Plan review schedules based on historical patterns"
            ]
        }