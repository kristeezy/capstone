   +-------------------+           +-------------------+
   |       User        |           |       Group       |
   +-------------------+           +-------------------+
   | PK  UserID        |<>-----o---| PK  GroupID       |
   |     Username      |           |     GroupName     |
   |     Phone         |           | FK  CreatorUserID |-----|
   |     Email         |           +-------------------+     |
   |     Password      |                                     |
   +-------------------+                                     |
         |                                                   |
         |                                                   |
         |                                                   |
         |                  +------------------------+       |
         o---o--------------|        Expense         |       |
                            +------------------------+       |
                            | PK  ExpenseID         |<------|
                            | FK  GroupID           |
                            | FK  PayerUserID       |----o
                            |     Description       |
                            |     Amount            |
                            |     Date              |
                            +------------------------+
                                   |
                                   |
                            +------------------------+
                            |  ExpenseParticipants  |
                            +------------------------+
                            | PK  ExpenseID, UserID |
                            | FK  ExpenseID         |
                            | FK  UserID            |
                            |     Share             |
                            +------------------------+
