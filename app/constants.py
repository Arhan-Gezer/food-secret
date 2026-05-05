# constants.py
# Everyone imports from here. Never hardcode these strings anywhere else.

# --- Session Keys ---
SESSION_USER_ID = "user_id"
SESSION_EMAIL = "email"
SESSION_NAME = "name"

# --- Meal Types ---
MEAL_BREAKFAST = "breakfast"
MEAL_LUNCH = "lunch"
MEAL_DINNER = "dinner"
MEAL_SNACK = "snack"

MEAL_TYPES = [MEAL_BREAKFAST, MEAL_LUNCH, MEAL_DINNER, MEAL_SNACK]

# --- Order Status ---
ORDER_PENDING = "pending"
ORDER_CONFIRMED = "confirmed"
ORDER_DELIVERED = "delivered"

ORDER_STATUSES = [ORDER_PENDING, ORDER_CONFIRMED, ORDER_DELIVERED]

# --- Gender ---
GENDER_MALE = "male"
GENDER_FEMALE = "female"

GENDERS = [GENDER_MALE, GENDER_FEMALE]

# --- Food Entry Types (Factory Pattern) ---
ENTRY_SIMPLE = "simple"
ENTRY_MACRO = "macro"

# --- Flash Message Categories ---
FLASH_SUCCESS = "success"
FLASH_ERROR = "error"
FLASH_INFO = "info"

# --- Error Messages ---
MSG_INVALID_CREDENTIALS = "Invalid email or password."
MSG_EMAIL_TAKEN = "This email address is already registered."
MSG_NOT_LOGGED_IN = "Please log in to access this page."
MSG_RECIPE_NOT_FOUND = "Recipe not found."
MSG_ORDER_NOT_FOUND = "Order not found."
MSG_INVALID_MEAL_TYPE = "Invalid meal type."
MSG_INVALID_ENTRY_TYPE = "Invalid food entry type. Use 'simple' or 'macro'."
MSG_MISSING_FIELDS = "Please fill in all required fields."

# --- Success Messages ---
MSG_REGISTER_SUCCESS = "Account created successfully. Please log in."
MSG_LOGIN_SUCCESS = "Welcome back!"
MSG_LOGOUT_SUCCESS = "You have been logged out."
MSG_RECIPE_CREATED = "Recipe created successfully."
MSG_CALORIES_LOGGED = "Calories logged successfully."
MSG_ORDER_PLACED = "Your order has been placed successfully."