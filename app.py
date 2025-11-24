from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import csv
import io
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///deliveries.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_id = db.Column(db.String(20), unique=True, nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_phone = db.Column(db.String(20), nullable=False)
    recipient_name = db.Column(db.String(100), nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    recipient_address = db.Column(db.String(200), nullable=False)
    delivery_person = db.Column(db.String(100), nullable=False)
    goods_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expenses = db.Column(db.Float, default=0.0)
    payment_by = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Delivery {self.display_id}>'

def generate_display_id():
    """Generate a unique display ID for new deliveries."""
    now = datetime.now()
    date_str = now.strftime('%y%m%d')
    
    # Get the last delivery for TODAY only to reset sequence daily
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_deliveries = Delivery.query.filter(Delivery.created_at >= today_start).order_by(Delivery.created_at.desc()).all()
    
    # Count deliveries made today to determine the next sequence number
    today_count = len(today_deliveries)
    next_sequence = today_count + 1
    
    return f"{date_str}{str(next_sequence).zfill(4)}"

def get_date_ranges():
    """Get common date ranges used throughout the application."""
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Week: Sunday to Saturday
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    
    # Month: First day to last day of current month
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        month_end = now.replace(year=now.year+1, month=1, day=1) - timedelta(microseconds=1)
    else:
        month_end = now.replace(month=now.month+1, day=1) - timedelta(microseconds=1)
    
    # Year: First day to last day of current year
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    year_end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    
    return {
        'today': (today, today_end),
        'week': (week_start, week_end),
        'month': (month_start, month_end),
        'year': (year_start, year_end),
        'all': (datetime(2000, 1, 1), today_end)  # All time from year 2000
    }

@app.route('/')
def index():
    """Render the dashboard with operational statistics and overview."""
    try:
        # Get all deliveries for statistics
        deliveries = Delivery.query.order_by(Delivery.created_at.desc()).all()
        
        # Calculate statistics
        total_deliveries = len(deliveries)
        pending_count = len([d for d in deliveries if d.status == 'Pending'])
        in_transit_count = len([d for d in deliveries if d.status == 'In Transit'])
        delivered_count = len([d for d in deliveries if d.status == 'Delivered'])
        
        # Active deliveries (pending + in transit)
        active_deliveries = pending_count + in_transit_count
        
        # Today's completed deliveries
        today = datetime.now().date()
        completed_today = len([d for d in deliveries if d.status == 'Delivered' and d.created_at.date() == today])
        
        # Monthly completion rate
        current_month = today.replace(day=1)
        month_deliveries = [d for d in deliveries if d.created_at.date() >= current_month]
        month_delivered = [d for d in month_deliveries if d.status == 'Delivered']
        completion_rate = round((len(month_delivered) / len(month_deliveries) * 100), 1) if month_deliveries else 0
        
        # Today's deliveries
        today_deliveries = [d for d in deliveries if d.created_at.date() == today]
        
        # Recent activities (last 10 deliveries with time ago)
        recent_activities = []
        for delivery in deliveries[:10]:
            time_ago = get_time_ago(delivery.created_at) if delivery.created_at else "Unknown"
            recent_activities.append({
                'display_id': delivery.display_id,
                'status': delivery.status,
                'time_ago': time_ago
            })
        
        return render_template('index.html', 
                             deliveries=deliveries,
                             total_deliveries=total_deliveries,
                             active_deliveries=active_deliveries,
                             completed_today=completed_today,
                             completion_rate=completion_rate,
                             pending_count=pending_count,
                             in_transit_count=in_transit_count,
                             delivered_count=delivered_count,
                             today_deliveries=today_deliveries,
                             recent_activities=recent_activities)
    except Exception as e:
        app.logger.error(f"Error loading dashboard: {str(e)}")
        flash('An error occurred while loading the dashboard.', 'danger')
        return render_template('index.html', 
                             deliveries=[],
                             total_deliveries=0,
                             active_deliveries=0,
                             completed_today=0,
                             completion_rate=0,
                             pending_count=0,
                             in_transit_count=0,
                             delivered_count=0,
                             today_deliveries=[],
                             recent_activities=[])

def get_time_ago(created_at):
    """Calculate time ago string for a datetime."""
    if not created_at:
        return "Unknown"
    
    now = datetime.now()
    diff = now - created_at
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

@app.route('/add_delivery', methods=['GET', 'POST'])
def add_delivery():
    """Handle adding a new delivery."""
    if request.method == 'POST':
        try:
            # Capture the exact current local time when saving
            current_time = datetime.now()
            
            delivery = Delivery(
                display_id=generate_display_id(),
                sender_name=request.form['sender_name'],
                sender_phone=request.form['sender_phone'],
                recipient_name=request.form['recipient_name'],
                recipient_phone=request.form['recipient_phone'],
                recipient_address=request.form['recipient_address'],
                delivery_person=request.form['delivery_person'],
                goods_type=request.form['goods_type'],
                quantity=int(request.form['quantity']),
                amount=float(request.form['amount']),
                expenses=float(request.form.get('expenses', 0.0)),
                payment_by=request.form['payment_by'],
                status=request.form.get('status', 'Pending'),
                created_at=current_time  # Explicitly set to current local time
            )
            db.session.add(delivery)
            db.session.commit()
            flash('Delivery added successfully!', 'success')
            return redirect(url_for('add_delivery'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error adding delivery: {str(e)}")
            flash('Error adding delivery. Please check the form and try again.', 'danger')
    return render_template('add_delivery.html')

@app.route('/update_status/<int:delivery_id>/<status>', methods=['GET', 'POST'])
def update_status(delivery_id, status):
    """Update the status of a delivery."""
    try:
        delivery = Delivery.query.get_or_404(delivery_id)
        delivery.status = status
        db.session.commit()
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({
                'success': True,
                'message': f'Delivery status updated to {status}',
                'new_status': status
            })
        else:
            flash(f'Delivery status updated to {status}', 'success')
            return redirect(url_for('index'))
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating status: {str(e)}")
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({
                'success': False,
                'error': 'Error updating status'
            }), 500
        else:
            flash('Error updating status', 'danger')
            return redirect(url_for('index'))

@app.route('/delete_delivery/<int:delivery_id>', methods=['DELETE'])
def delete_delivery(delivery_id):
    """Delete a delivery."""
    try:
        delivery = Delivery.query.get_or_404(delivery_id)
        db.session.delete(delivery)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Delivery deleted successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting delivery: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/reports')
def reports():
    """Render the reports page."""
    try:
        # Get recent deliveries (last 10)
        recent_deliveries = Delivery.query.order_by(Delivery.created_at.desc()).limit(10).all()
        return render_template('reports.html', recent_deliveries=recent_deliveries)
    except Exception as e:
        app.logger.error(f"Error loading reports page: {str(e)}", exc_info=True)
        return render_template('reports.html', recent_deliveries=[])

@app.route('/get_delivery_persons')
def get_delivery_persons():
    """Get delivery persons and their delivery counts for a specific period."""
    try:
        # Get period parameter from query string
        period = request.args.get('period', 'month')
        
        # Get date ranges for filtering
        date_ranges = get_date_ranges()
        start_date, end_date = date_ranges.get(period, (date_ranges['month'][0], date_ranges['month'][1]))
        
        # Get all deliveries with non-empty delivery person within the date range
        deliveries = Delivery.query.filter(
            Delivery.delivery_person.isnot(None) & 
            (Delivery.delivery_person != '') &
            (Delivery.created_at >= start_date) &
            (Delivery.created_at <= end_date)
        ).all()
        
        # Group by delivery person and collect detailed info
        person_stats = {}
        for delivery in deliveries:
            person = delivery.delivery_person
            if person not in person_stats:
                person_stats[person] = {
                    'total': 0,
                    'delivered': 0,
                    'pending': 0,
                    'in_transit': 0,
                    'revenue': 0.0,
                    'expenses': 0.0,
                    'display_ids': []
                }
            
            person_stats[person]['total'] += 1
            person_stats[person]['revenue'] += delivery.amount
            person_stats[person]['expenses'] += delivery.expenses
            person_stats[person]['display_ids'].append(delivery.display_id)
            
            if delivery.status == 'Delivered':
                person_stats[person]['delivered'] += 1
            elif delivery.status == 'Pending':
                person_stats[person]['pending'] += 1
            elif delivery.status == 'In Transit':
                person_stats[person]['in_transit'] += 1
        
        # Convert to list and sort by total deliveries (descending)
        result = []
        for person, stats in sorted(person_stats.items(), 
                                 key=lambda x: x[1]['total'], reverse=True):
            net_profit = stats['revenue'] - stats['expenses']
            result.append({
                'name': person,
                'total_deliveries': stats['total'],
                'delivered': stats['delivered'],
                'pending': stats['pending'],
                'in_transit': stats['in_transit'],
                'revenue': stats['revenue'],
                'expenses': stats['expenses'],
                'net_profit': net_profit,
                'display_ids': stats['display_ids'],
                'success_rate': ((stats['delivered'] * 1.0 + stats['in_transit'] * 0.5) / stats['total'] * 100) if stats['total'] > 0 else 0
            })
        
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error getting delivery persons: {str(e)}")
        return jsonify([])

@app.route('/get_summary')
def get_summary():
    """Get summary statistics for deliveries."""
    try:
        dates = get_date_ranges()
        
        # Get all deliveries for detailed filtering
        all_deliveries = Delivery.query.order_by(Delivery.created_at.desc()).all()
        
        # Convert deliveries to dictionary format for JSON response
        deliveries_data = []
        for delivery in all_deliveries:
            delivery_dict = {
                'id': delivery.id,
                'display_id': delivery.display_id,
                'sender_name': delivery.sender_name,
                'recipient_name': delivery.recipient_name,
                'status': delivery.status,
                'amount': float(delivery.amount) if delivery.amount else 0.0,
                'expenses': float(delivery.expenses) if delivery.expenses else 0.0,
                'delivery_person': delivery.delivery_person or '',
                'created_at': delivery.created_at.isoformat() if delivery.created_at else None
            }
            deliveries_data.append(delivery_dict)
        
        def get_summary_data(query):
            """Helper function to get summary data for a query."""
            deliveries = query.all()
            total_amount = sum(d.amount for d in deliveries)
            total_expenses = sum(d.expenses for d in deliveries)
            return {
                'total_deliveries': len(deliveries),
                'total_amount': total_amount,
                'total_expenses': total_expenses,
                'net_profit': total_amount - total_expenses,
                'pending': len([d for d in deliveries if d.status == 'Pending']),
                'in_transit': len([d for d in deliveries if d.status == 'In Transit']),
                'delivered': len([d for d in deliveries if d.status == 'Delivered'])
            }
        
        return jsonify({
            'deliveries': deliveries_data,  # Add individual delivery records
            'today': get_summary_data(Delivery.query.filter(Delivery.created_at >= dates['today'][0])),
            'week': get_summary_data(Delivery.query.filter(Delivery.created_at >= dates['week'][0])),
            'month': get_summary_data(Delivery.query.filter(Delivery.created_at >= dates['month'][0])),
            'year': get_summary_data(Delivery.query.filter(Delivery.created_at >= dates['year'][0]))
        })
    except Exception as e:
        app.logger.error(f"Error getting summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/export/<period>')
def export(period):
    """Export deliveries data as CSV for the specified period."""
    try:
        date_ranges = get_date_ranges()
        
        # Define date ranges using the new format
        if period == 'daily':
            start_date, end_date = date_ranges['today']
            filename = f'deliveries_{datetime.now().strftime("%Y-%m-%d")}.csv'
            date_range = 'today'
        elif period == 'weekly':
            start_date, end_date = date_ranges['week']
            filename = f'deliveries_week_{datetime.now().strftime("%Y-%U")}.csv'
            date_range = 'this week'
        elif period == 'monthly':
            start_date, end_date = date_ranges['month']
            filename = f'deliveries_{datetime.now().strftime("%Y-%m")}.csv'
            date_range = 'this month'
        else:  # yearly
            start_date, end_date = date_ranges['year']
            filename = f'deliveries_{datetime.now().year}.csv'
            date_range = 'this year'
        
        # Query deliveries
        deliveries = Delivery.query.filter(
            Delivery.created_at.between(start_date, end_date)
        ).order_by(Delivery.created_at.desc()).all()
        
        if not deliveries:
            flash(f'No delivery records found for {date_range}.', 'info')
            return redirect(url_for('reports'))
        
        # Generate CSV
        si = io.StringIO()
        writer = csv.writer(si)
        
        # Write header
        writer.writerow([
            'ID', 'Display ID', 'Sender', 'Recipient', 'Delivery Person',
            'Goods Type', 'Quantity', 'Amount (KSh)', 'Expenses (KSh)', 'Profit (KSh)', 'Status', 'Created At'
        ])
        
        # Write data
        for delivery in deliveries:
            profit = delivery.amount - delivery.expenses
            writer.writerow([
                str(delivery.id),
                f"'{delivery.display_id}",
                delivery.sender_name,
                delivery.recipient_name,
                delivery.delivery_person,
                delivery.goods_type,
                delivery.quantity,
                f"{delivery.amount:.2f}",
                f"{delivery.expenses:.2f}",
                f"{profit:.2f}",
                delivery.status,
                delivery.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        # Create response
        response = make_response(si.getvalue().encode('utf-8'))
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-type'] = 'text/csv; charset=utf-8'
        return response
        
    except Exception as e:
        app.logger.error(f"Error exporting {period} data: {str(e)}", exc_info=True)
        flash(f'Error exporting {period} data: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/get_delivery_details/<int:delivery_id>')
def get_delivery_details(delivery_id):
    """Get detailed information for a specific delivery."""
    try:
        delivery = Delivery.query.get(delivery_id)
        if not delivery:
            return jsonify({'error': 'Delivery not found'}), 404
        
        # Convert delivery to dictionary for JSON response - only use existing fields
        delivery_data = {
            'id': delivery.id,
            'display_id': delivery.display_id,
            'sender_name': delivery.sender_name,
            'sender_phone': delivery.sender_phone,
            'sender_address': '',  # Field doesn't exist in model
            'recipient_name': delivery.recipient_name,
            'recipient_phone': delivery.recipient_phone,
            'recipient_address': delivery.recipient_address,
            'status': delivery.status,
            'amount': delivery.amount,
            'expenses': delivery.expenses,
            'delivery_person': delivery.delivery_person,
            'notes': '',  # Field doesn't exist in model
            'goods_type': delivery.goods_type,
            'quantity': delivery.quantity,
            'payment_by': delivery.payment_by,
            'created_at': delivery.created_at.isoformat() if delivery.created_at else None,
            'updated_at': delivery.created_at.isoformat() if delivery.created_at else None  # Use created_at since updated_at doesn't exist
        }
        
        return jsonify(delivery_data)
        
    except Exception as e:
        app.logger.error(f"Error getting delivery details for ID {delivery_id}: {str(e)}")
        return jsonify({'error': 'Failed to load delivery details'}), 500

@app.route('/get_recent_deliveries')
def get_recent_deliveries():
    """Get recent deliveries for the Recent Deliveries section."""
    try:
        # Get recent deliveries (last 10)
        recent_deliveries = Delivery.query.order_by(Delivery.created_at.desc()).limit(10).all()
        
        # Convert to list of dictionaries
        deliveries_data = []
        for delivery in recent_deliveries:
            delivery_dict = {
                'id': delivery.id,
                'display_id': delivery.display_id,
                'sender_name': delivery.sender_name,
                'sender_phone': delivery.sender_phone,
                'recipient_name': delivery.recipient_name,
                'recipient_phone': delivery.recipient_phone,
                'recipient_address': delivery.recipient_address,
                'status': delivery.status,
                'amount': float(delivery.amount) if delivery.amount else 0.0,
                'expenses': float(delivery.expenses) if delivery.expenses else 0.0,
                'delivery_person': delivery.delivery_person or '',
                'goods_type': delivery.goods_type,
                'quantity': delivery.quantity,
                'payment_by': delivery.payment_by,
                'created_at': delivery.created_at.isoformat() if delivery.created_at else None
            }
            deliveries_data.append(delivery_dict)
        
        return jsonify(deliveries_data)
        
    except Exception as e:
        app.logger.error(f"Error getting recent deliveries: {str(e)}")
        return jsonify({'error': 'Failed to load recent deliveries'}), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)