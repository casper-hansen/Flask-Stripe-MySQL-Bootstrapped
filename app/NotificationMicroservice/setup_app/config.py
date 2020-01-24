MODE='Testing'
DEBUG=True

if MODE == 'Testing':
    # For MacOS, this fixes an issue where you can't reach other endpoints on localhost
    MYSQL_HOST='host.docker.internal'
    BASE_URL='host.docker.internal'
else:
    MYSQL_HOST='localhost'
    BASE_URL='localhost'

MYSQL_PORT='5001'
MYSQL_USER="root"
MYSQL_PASSWORD="rootpw"
MYSQL_DB_NAME="UserDB"

TRIAL_LENGTH_DAYS=1
SQLALCHEMY_TRACK_MODIFICATIONS=False
PROTOCOL='http'
SECRET_KEY='super secret string'

# Public and secret keys for stripe to validate
# https://dashboard.stripe.com/dashboard
STRIPE_PUBLIC_KEY='pk_test_H9P7ybsV5u43G5tmKcBqYqSZ007jr2J6zD'
STRIPE_SECRET_KEY='sk_test_wSMfrRKnGyFpDlH6GMMfaDEo00Jizg9GJh'

# Make a product and make plans for the product
# https://dashboard.stripe.com/subscriptions/products
STRIPE_PLAN_STARTER='plan_GLXg9InyA37U3l'
STRIPE_PLAN_GROWTH='plan_GLXgiOgfPpscMY'
STRIPE_PLAN_SCALE='plan_GLXgHjFavnxdBA'

# Configure three endpoints; checkout.session.completed, invoice.payment_succeeded, customer.subscription.deleted
# https://dashboard.stripe.com/webhooks
WEBHOOK_CHECKOUT_SESSION_COMPLETED='whsec_26zKj4jFtnrsF6LVgCvJxp4dilM4Bo73'
WEBHOOK_INVOICE_PAYMENT_SUCCEEDED='whsec_VlSaqc1aVmcYK5BQoQat5fEiFxfHzxv9'
WEBHOOK_CUSTOMER_SUBSCRIPTION_DELETED='whsec_gIXe1MTEkNTp4cZMzIknS6uU1kosNKUy'

# Ports for the microservices
FRONTEND_PORT='5000'
NOTIFICATION_PORT='5002'
USER_PORT='5003'
STRIPE_PORT='5004'