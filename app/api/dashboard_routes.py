from flask import request, jsonify
from app.services.dashboard_service import DashboardService


def register_dashboard_routes(app):
    @app.route("/api/dashboard", methods=["GET"])
    def get_dashboard_data():
        """Get dashboard data for the current user."""
        user_id = request.args.get("user_id", type=int)
        
        if not user_id:
            return jsonify({"error": "user_id is required as a query parameter"}), 400
        
        try:
            dashboard = DashboardService.get_dashboard_data(user_id)
            return jsonify({
                "message": "Dashboard data retrieved successfully",
                **dashboard.to_dict()
            }), 200
        except Exception as e:
            print(f"Error getting dashboard data: {e}")
            return jsonify({"error": "An unexpected error occurred"}), 500

