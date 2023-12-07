# capstone
1. Goal of the Website:
The primary goal of our website is to provide users with a seamless platform for managing shared expenses in a group setting. Users can create groups, add expenses, and easily calculate and distribute costs among group members using the Splitwise API. The website aims to simplify the process of tracking shared expenses and settling debts within a group.
2. Target Users:
The target users for our website are individuals who frequently share expenses with friends, roommates, or colleagues. The demographic includes young adults, professionals, and anyone involved in group activities where expenses need to be managed efficiently. The users should have a basic understanding of splitting costs and be comfortable using a web-based application.
3. Data Usage:
The website will utilize data from the Splitwise API, which includes information about groups, expenses, and user details. The essential data points involve user profiles, expense details (amount, description, date), and group information. Additionally, user authentication data will be stored securely to ensure a personalized and secure experience.
4. Project Approach:
a. Database Schema:
User Table (UserID, Username, Phone, Email, Password)
Group Table (GroupID, GroupName, CreatorUserID)
Expense Table (ExpenseID, GroupID, Description, Amount, Date, PayerUserID)
ExpenseParticipants Table (ExpenseID, UserID, Share)
b. API Issues:
Ensure proper error handling for API responses.
Regularly check for updates or changes in the Splitwise API.
c. Security Measures:
Implement secure user authentication and authorization.
Encrypt sensitive information, such as user passwords.
Utilize HTTPS to secure data transmission.
d. Functionality:
User registration and authentication.
Group creation and management.
Adding expenses to groups.
Real-time calculation of each user's share.
SMS integration for notifying users of their share.
History of expenses and settlements.
e. User Flow:
User registers or logs in.
Creates a group or joins an existing one.
Adds expenses to the group, specifying participants.
System calculates each participant's share.
Users receive SMS notifications with their share.
f. Features Beyond CRUD:
Real-time expense calculation.
SMS integration for notifications.
Expense history and summary.
User-friendly interface for a seamless experience.
