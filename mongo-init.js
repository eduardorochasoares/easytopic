db.createUser(
        {
            user: "root",
            roles: [
                {
                    role: "root",
                    db: "topic_segmentation"
                }
            ]
        }
);