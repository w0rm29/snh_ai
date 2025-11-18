drop table if exists nodes;

create table nodes (
   id        integer primary key,
   label     text not null,
   parent_id integer,
   foreign key ( parent_id )
      references nodes ( id )
);