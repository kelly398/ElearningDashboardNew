QUESTION_POOL_SEED = [
    {
        "title": "Python Foundations Quiz",
        "module_title": "Python Foundations",
        "description": "Variables, functions, and Python best practices.",
        "topic": "Python",
        "difficulty_pools": {
            "easy": [
                {"question": "Which keyword defines a function in Python?", "options": ["func", "define", "def", "lambda"], "answer": "def"},
                {"question": "What data type is returned by input()?", "options": ["int", "float", "str", "bool"], "answer": "str"},
                {"question": "Which symbol starts a comment?", "options": ["//", "#", "--", "/*"], "answer": "#"},
                {"question": "Which function displays output to the console?", "options": ["echo()", "print()", "display()", "console.log"], "answer": "print()"},
                {"question": "What is the boolean result of 3 == '3'?", "options": ["True", "False", "None", "TypeError"], "answer": "False"}
            ],
            "medium": [
                {"question": "Which loop runs while a condition remains True?", "options": ["for", "while", "loop", "iterate"], "answer": "while"},
                {"question": "List comprehension is useful for?", "options": ["Building lists concisely", "Writing classes", "Managing memory", "Debugging"], "answer": "Building lists concisely"},
                {"question": "What does slicing [:-1] do?", "options": ["Skips first element", "Removes last element", "Reverses list", "Duplicates list"], "answer": "Removes last element"},
                {"question": "Which keyword handles exceptions?", "options": ["catch", "rescue", "try", "handle"], "answer": "try"},
                {"question": "What is returned when a function has no return statement?", "options": ["0", "", "None", "False"], "answer": "None"}
            ],
            "hard": [
                {"question": "What does *args capture?", "options": ["Keyword arguments", "Positional arguments tuple", "Dictionary", "Defaults"], "answer": "Positional arguments tuple"},
                {"question": "Which decorator preserves metadata when wrapping functions?", "options": ["@wraps", "@cached", "@staticmethod", "@property"], "answer": "@wraps"},
                {"question": "What does yield create?", "options": ["Coroutine", "Generator", "Lambda", "Context manager"], "answer": "Generator"},
                {"question": "Which module manages virtual environments?", "options": ["venv", "pip", "sys", "argparse"], "answer": "venv"},
                {"question": "Membership check in a Python set is?", "options": ["O(n)", "O(log n)", "O(1) average", "O(n log n)"], "answer": "O(1) average"}
            ]
        }
    },
    {
        "title": "SQL Basics Quiz",
        "module_title": "SQL Basics",
        "description": "Foundational SELECT/WHERE and aggregation.",
        "topic": "SQL",
        "difficulty_pools": {
            "easy": [
                {"question": "Which clause specifies the table to read from?", "options": ["SELECT", "FROM", "WHERE", "GROUP"], "answer": "FROM"},
                {"question": "Which keyword removes duplicates?", "options": ["UNIQUE", "DISTINCT", "FILTER", "CLEAN"], "answer": "DISTINCT"},
                {"question": "What does WHERE do?", "options": ["Sort rows", "Filter rows", "Create columns", "Count rows"], "answer": "Filter rows"},
                {"question": "Which aggregate counts rows?", "options": ["SUM", "AVG", "COUNT", "MIN"], "answer": "COUNT"},
                {"question": "Which operator matches partial strings?", "options": ["IN", "LIKE", "BETWEEN", "EXISTS"], "answer": "LIKE"}
            ],
            "medium": [
                {"question": "Which clause groups rows before aggregation?", "options": ["GROUP BY", "ORDER BY", "HAVING", "LIMIT"], "answer": "GROUP BY"},
                {"question": "HAVING is evaluated after which clause?", "options": ["SELECT", "WHERE", "GROUP BY", "FROM"], "answer": "GROUP BY"},
                {"question": "Which join returns only matching rows?", "options": ["LEFT", "RIGHT", "FULL", "INNER"], "answer": "INNER"},
                {"question": "What does BETWEEN 10 AND 20 include?", "options": ["10 only", "20 only", "10 and 20 inclusive", "Exclusive range"], "answer": "10 and 20 inclusive"},
                {"question": "Which command changes data in a table?", "options": ["ALTER", "INSERT", "UPDATE", "SELECT"], "answer": "UPDATE"}
            ],
            "hard": [
                {"question": "What does EXISTS check for?", "options": ["Column existence", "Row existence in subquery", "Table creation", "Index usage"], "answer": "Row existence in subquery"},
                {"question": "Which clause enforces ordering?", "options": ["SORT BY", "ORDER BY", "GROUP BY", "ALIGN BY"], "answer": "ORDER BY"},
                {"question": "How do you alias a column?", "options": ["col -> alias", "col alias", "col AS alias", "col = alias"], "answer": "col AS alias"},
                {"question": "Which isolation level prevents dirty reads?", "options": ["Read Uncommitted", "Read Committed", "Chaos", "None"], "answer": "Read Committed"},
                {"question": "What is a window function?", "options": ["Aggregate entire table", "Function using OVER() on partitions", "Stored procedure", "Trigger"], "answer": "Function using OVER() on partitions"}
            ]
        }
    },
    {
        "title": "Data Visualization Quiz",
        "module_title": "Data Visualization",
        "description": "Best practices for plotting insights.",
        "topic": "Data Visualization",
        "difficulty_pools": {
            "easy": [
                {"question": "Which plot shows parts of a whole?", "options": ["Histogram", "Pie chart", "Scatter", "Box"], "answer": "Pie chart"},
                {"question": "Base library for charts in Python?", "options": ["NumPy", "Matplotlib", "Pandas", "TensorFlow"], "answer": "Matplotlib"},
                {"question": "Which chart shows distribution over bins?", "options": ["Line chart", "Histogram", "Heatmap", "Pie"], "answer": "Histogram"},
                {"question": "Which palette avoids red-green issues?", "options": ["Random", "Colorblind-friendly", "Rainbow", "Classic"], "answer": "Colorblind-friendly"},
                {"question": "Which chart compares two numeric variables?", "options": ["Scatter plot", "Pie chart", "Tree map", "Sankey"], "answer": "Scatter plot"}
            ],
            "medium": [
                {"question": "Which Seaborn function shows categories vs numeric with boxes?", "options": ["barplot", "boxplot", "violinplot", "heatmap"], "answer": "boxplot"},
                {"question": "What does a heatmap encode?", "options": ["Images", "Matrix values / correlations", "Audio", "Video"], "answer": "Matrix values / correlations"},
                {"question": "Why annotate points?", "options": ["Decoration", "Highlight key values", "Increase file size", "Hide noise"], "answer": "Highlight key values"},
                {"question": "Which chart shows trend over time best?", "options": ["Line chart", "Pie chart", "Tree map", "Radar"], "answer": "Line chart"},
                {"question": "Facet grids help with?", "options": ["Comparing subsets", "Data encryption", "CSS styling", "SQL queries"], "answer": "Comparing subsets"}
            ],
            "hard": [
                {"question": "Which chart shows hierarchical data best?", "options": ["Scatter", "Treemap", "Pie", "Line"], "answer": "Treemap"},
                {"question": "When use log scales?", "options": ["Never", "When range spans orders of magnitude", "For tiny datasets", "Night mode"], "answer": "When range spans orders of magnitude"},
                {"question": "What is chart junk?", "options": ["Useful labels", "Unnecessary clutter", "Legends", "Axes"], "answer": "Unnecessary clutter"},
                {"question": "Which chart shows flow between categories?", "options": ["Sankey diagram", "Box plot", "Histogram", "Violin"], "answer": "Sankey diagram"},
                {"question": "Why use small multiples?", "options": ["Isolate variables", "Show randomness", "Increase color palette", "Hide data"], "answer": "Isolate variables"}
            ]
        }
    },
    {
        "title": "Cloud Computing Quiz",
        "module_title": "Cloud Computing",
        "description": "Assess core cloud concepts.",
        "topic": "Cloud Computing",
        "difficulty_pools": {
            "easy": [
                {"question": "What does SaaS stand for?", "options": ["Software as a Service", "Storage as a Service", "Security as a Service", "Server as a Service"], "answer": "Software as a Service"},
                {"question": "Which model lets you rent VMs?", "options": ["IaaS", "SaaS", "PaaS", "FaaS"], "answer": "IaaS"},
                {"question": "AWS EC2 is an example of?", "options": ["SaaS", "IaaS", "PaaS", "On-prem"], "answer": "IaaS"},
                {"question": "Which storage is object storage?", "options": ["Amazon S3", "Amazon EC2", "AWS Lambda", "Amazon RDS"], "answer": "Amazon S3"},
                {"question": "Who offers Azure?", "options": ["Google", "Microsoft", "Amazon", "IBM"], "answer": "Microsoft"}
            ],
            "medium": [
                {"question": "What does PaaS primarily provide?", "options": ["Hardware only", "Full apps", "Managed runtimes and tools", "Networking gear"], "answer": "Managed runtimes and tools"},
                {"question": "Which AWS service runs code serverlessly?", "options": ["EC2", "Lambda", "EBS", "Route53"], "answer": "Lambda"},
                {"question": "A VPC provides?", "options": ["Physical servers", "Isolated network", "Database backups", "User identities"], "answer": "Isolated network"},
                {"question": "Which service caches content globally?", "options": ["CloudFront", "RDS", "SQS", "Glue"], "answer": "CloudFront"},
                {"question": "Auto Scaling does what?", "options": ["Encrypts data", "Monitors logs", "Adjusts compute capacity", "Adds IAM users"], "answer": "Adjusts compute capacity"}
            ],
            "hard": [
                {"question": "Cloud bursting handles?", "options": ["Database migrations", "Peak workloads via public cloud spillover", "Billing", "DNS"], "answer": "Peak workloads via public cloud spillover"},
                {"question": "Managed Kubernetes on AWS is?", "options": ["ECS", "EKS", "Fargate", "Lightsail"], "answer": "EKS"},
                {"question": "Multi-tenancy ensures?", "options": ["Single tenant only", "Multiple customers share resources securely", "Only on-prem", "No virtualization"], "answer": "Multiple customers share resources securely"},
                {"question": "Snowball is used for?", "options": ["Serverless compute", "Large data transfers", "Cost reporting", "Chat"], "answer": "Large data transfers"},
                {"question": "Spot instances are ideal for?", "options": ["Mission-critical DBs", "Low-cost interruptible workloads", "Billing dashboards", "Long-running dedicated servers"], "answer": "Low-cost interruptible workloads"}
            ]
        }
    },
    {
        "title": "Web Design with JavaScript Quiz",
        "module_title": "Web Design with JavaScript",
        "description": "JavaScript and front-end fundamentals.",
        "topic": "Web Design with JavaScript",
        "difficulty_pools": {
            "easy": [ ... truncated ... ]
]
