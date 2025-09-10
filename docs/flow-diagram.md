%%{init: {"flowchart": {"htmlLabels": false}} }%%
graph TD
%% User Interactions
A[👤 User Interaction] --> B{Type of Interaction}
B -->|Button Press| C[📱 Callback Query]
B -->|Text Message| D[💬 Text Message]

    %% Button Press Flow
    C --> E[📨 Telegram Bot Receives callback_query]
    E --> F[🎯 MainClient.on_callback]
    F --> G[📋 Extract query.data]
    G --> H{PreferencesHandler can handle?}

    H -->|Yes| I[🎛️ PreferencesHandler.handle_callback]
    H -->|No| J{Main Navigation?}

    J -->|menu_main| K[🏠 Show Main Menu]
    J -->|preferences_menu| L[⚙️ Show Preferences Menu]
    J -->|menu_availability| M[📅 Show Availability Menu]
    J -->|menu_docs| N[📝 Show Docs Menu]
    J -->|Other| O[❓ Unknown Command]

    %% PreferencesHandler Routing
    I --> P{Callback Type}
    P -->|shift_times_*| Q[⏰ Route to ShiftTimesHandler]
    P -->|reminders_*| R[🔔 Route to RemindersHandler]
    P -->|timezone_*| S[🌍 Route to TimezoneHandler]

    %% ShiftTimesHandler Button Flow
    Q --> T[🎯 ShiftTimesHandler.handle_callback]
    T --> U{Action Type}
    U -->|show_shift_times| V[📋 Show Shift Times Menu]
    U -->|edit_start_morning| W[🌅 Edit Morning Start Time]
    U -->|edit_end_morning| X[🌅 Edit Morning End Time]
    U -->|edit_start_afternoon| Y[🌇 Edit Afternoon Start Time]
    U -->|edit_end_afternoon| Z[🌇 Edit Afternoon End Time]
    U -->|edit_start_night| AA[🌙 Edit Night Start Time]
    U -->|edit_end_night| AB[🌙 Edit Night End Time]
    U -->|reset_defaults| AC[🔄 Reset to Defaults]

    %% Text Input Flow
    D --> AD[📨 Telegram Bot Receives message]
    AD --> AE[🎯 MainClient.on_message]
    AE --> AF{PreferencesHandler can handle text?}
    AF -->|Yes| AG[🎛️ PreferencesHandler.handle_text_input]
    AF -->|No| AH[❓ Unknown Text Message]

    %% PreferencesHandler Text Routing
    AG --> AI{Which Handler Waiting?}
    AI -->|shift_times| AJ[⏰ Route to ShiftTimesHandler]
    AI -->|reminders| AK[🔔 Route to RemindersHandler]
    AI -->|timezone| AL[🌍 Route to TimezoneHandler]

    %% ShiftTimesHandler Text Flow
    AJ --> AM[🎯 ShiftTimesHandler.handle_text_input]
    AM --> AN{Validate Time Format}
    AN -->|Valid| AO[✅ Time Valid]
    AN -->|Invalid| AP[❌ Time Invalid]

    AO --> AQ[💾 Save New Time]
    AQ --> AR[✨ Show Success Confirmation]
    AR --> AS[📋 Return to Shift Times Menu]

    AP --> AT[⚠️ Show Error Message]
    AT --> AU[🔄 Ask for Time Again]

    %% State Management
    W --> AV[📝 Set waiting_for: morning_start]
    X --> AW[📝 Set waiting_for: morning_end]
    Y --> AX[📝 Set waiting_for: afternoon_start]
    Z --> AY[📝 Set waiting_for: afternoon_end]
    AA --> AZ[📝 Set waiting_for: night_start]
    AB --> BA[📝 Set waiting_for: night_end]

    AV --> BB[📨 Ask for Morning Start Time]
    AW --> BC[📨 Ask for Morning End Time]
    AX --> BD[📨 Ask for Afternoon Start Time]
    AY --> BE[📨 Ask for Afternoon End Time]
    AZ --> BF[📨 Ask for Night Start Time]
    BA --> BG[📨 Ask for Night End Time]

    %% Styling
    classDef userAction fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef mainClient fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef preferencesHandler fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef shiftHandler fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef textFlow fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef stateManagement fill:#f1f8e9,stroke:#558b2f,stroke-width:2px

    %% Assign classes (no overlaps)
    class A,B,C,D userAction
    class F,AE,K,L,M,N,O,AH mainClient
    class I,AG,AI preferencesHandler
    class Q,T,U,V,W,X,Y,Z,AA,AB,AC,AM,AN,AO,AP,AQ,AR,AS,AT,AU shiftHandler
    class D,AD,AE,AF textFlow
    class AV,AW,AX,AY,AZ,BA,BB,BC,BD,BE,BF,BG stateManagement
