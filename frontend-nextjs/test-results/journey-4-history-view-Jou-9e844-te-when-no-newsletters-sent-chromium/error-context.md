# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e3]:
    - link "CP CreatorPulse" [ref=e5] [cursor=pointer]:
      - /url: /
      - generic [ref=e6]: CP
      - text: CreatorPulse
    - generic [ref=e7]:
      - generic [ref=e8]:
        - heading "Create your account" [level=2] [ref=e9]
        - paragraph [ref=e10]: Get started with your AI newsletter today
      - generic [ref=e11]:
        - generic [ref=e12]:
          - generic [ref=e13]:
            - text: Name
            - textbox "Name" [ref=e14]:
              - /placeholder: John Doe
          - generic [ref=e15]:
            - text: Email
            - textbox "Email" [ref=e16]:
              - /placeholder: you@example.com
          - generic [ref=e17]:
            - text: Password
            - textbox "Password" [ref=e18]:
              - /placeholder: ••••••••
            - paragraph [ref=e19]: Must be at least 8 characters
          - button "Create Account" [ref=e20]
        - generic [ref=e21]:
          - text: Already have an account?
          - link "Sign in" [ref=e22] [cursor=pointer]:
            - /url: /login
  - region "Notifications (F8)":
    - list
```